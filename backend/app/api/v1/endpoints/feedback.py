"""
Feedback Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from uuid import UUID
import pandas as pd
import io
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Feedback, User
from app.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackUpdate,
    BatchUploadResponse
)
from app.services.ai_analyzer import get_ai_analyzer
from app.services.s3_service import s3_service
from app.tasks.analysis_tasks import analyze_feedback_task

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new feedback and analyze it"""
    
    # Create feedback record
    db_feedback = Feedback(
        tenant_id=current_user.get("tenant_id"),
        text=feedback_data.text,
        customer_id=feedback_data.customer_id,
        customer_name=feedback_data.customer_name,
        customer_email=feedback_data.customer_email,
        source=feedback_data.source,
        channel=feedback_data.channel,
        metadata=feedback_data.metadata
    )
    
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    
    # Schedule background analysis
    background_tasks.add_task(analyze_feedback_task, str(db_feedback.id))
    
    return db_feedback


@router.post("/bulk", response_model=BatchUploadResponse)
async def bulk_upload_feedback(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bulk upload feedback from CSV/Excel file (Admin and Analyst only)"""
    
    # Check if user has permission to upload (admin or analyst)
    user_role = current_user.get("role")
    if user_role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and analysts can upload feedback files"
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Store file in S3 if enabled (AWS Free Tier: 5GB storage)
        s3_key = None
        if s3_service.enabled:
            try:
                file_obj = io.BytesIO(contents)
                s3_result = await s3_service.upload_file_async(
                    file_obj,
                    file.filename,
                    current_user.get("tenant_id"),
                    prefix="bulk_uploads",
                    content_type=file.content_type,
                    metadata={
                        "uploaded_by": current_user.get("email", ""),
                        "upload_date": pd.Timestamp.now().isoformat()
                    }
                )
                s3_key = s3_result['key']
            except Exception as s3_error:
                # Log but don't fail - continue with processing
                print(f"S3 upload failed: {s3_error}")
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Use CSV, Excel, or JSON."
            )
        
        # Validate required columns
        required_columns = ['text']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns. Need: {required_columns}"
            )
        
        # Create feedback records
        feedback_ids = []
        for _, row in df.iterrows():
            feedback_metadata = row.to_dict()
            if s3_key:
                feedback_metadata['s3_key'] = s3_key  # Link to original file
            
            db_feedback = Feedback(
                tenant_id=current_user.get("tenant_id"),
                text=row['text'],
                customer_id=row.get('customer_id'),
                customer_name=row.get('customer_name'),
                customer_email=row.get('customer_email'),
                source=row.get('source', 'bulk_upload'),
                channel=row.get('channel'),
                metadata=feedback_metadata
            )
            db.add(db_feedback)
            await db.flush()
            feedback_ids.append(str(db_feedback.id))
        
        await db.commit()
        
        # Schedule background analysis for all feedback
        for feedback_id in feedback_ids:
            background_tasks.add_task(analyze_feedback_task, feedback_id)
        
        return {
            "job_id": f"bulk_{current_user.get('sub')}_{len(feedback_ids)}",
            "total_items": len(feedback_ids),
            "status": "processing",
            "message": f"Successfully uploaded {len(feedback_ids)} feedback items. Analysis in progress.",
            "s3_stored": s3_key is not None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/", response_model=List[FeedbackResponse])
async def list_feedback(
    skip: int = 0,
    limit: int = 50,
    sentiment: Optional[str] = None,
    urgency_level: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List feedback with filters"""
    
    query = select(Feedback).where(
        Feedback.tenant_id == current_user.get("tenant_id")
    )
    
    # Apply filters
    if sentiment:
        query = query.where(Feedback.sentiment == sentiment)
    if urgency_level:
        query = query.where(Feedback.urgency_level == urgency_level)
    if status:
        query = query.where(Feedback.status == status)
    
    # Order by created date (newest first)
    query = query.order_by(desc(Feedback.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    return feedbacks


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific feedback by ID"""
    
    result = await db.execute(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.tenant_id == current_user.get("tenant_id")
        )
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return feedback


@router.patch("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: UUID,
    feedback_update: FeedbackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update feedback status or categories"""
    
    result = await db.execute(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.tenant_id == current_user.get("tenant_id")
        )
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Update fields
    update_data = feedback_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete feedback"""
    
    result = await db.execute(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.tenant_id == current_user.get("tenant_id")
        )
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    await db.delete(feedback)
    await db.commit()
    
    return None


@router.post("/{feedback_id}/analyze", response_model=FeedbackResponse)
async def reanalyze_feedback(
    feedback_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger re-analysis of feedback"""
    
    result = await db.execute(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.tenant_id == current_user.get("tenant_id")
        )
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Schedule re-analysis
    background_tasks.add_task(analyze_feedback_task, str(feedback_id))
    
    return feedback
