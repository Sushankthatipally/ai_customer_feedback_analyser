"""
Clustering API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.models import Feedback
from app.services.clustering_service import get_clustering_service
from app.core.security import get_current_user

router = APIRouter()


@router.post("/run", response_model=Dict[str, Any])
async def run_clustering(
    n_clusters: int = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run clustering on all analyzed feedback
    """
    # Get all analyzed feedback with embeddings
    query = select(Feedback).where(
        Feedback.tenant_id == current_user.get("tenant_id"),
        Feedback.analyzed_at.isnot(None),
        Feedback.embedding.isnot(None)
    )
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    if len(feedbacks) < 5:
        raise HTTPException(
            status_code=400,
            detail="Not enough analyzed feedback for clustering (minimum 5 required)"
        )
    
    # Extract embeddings and texts
    embeddings = [f.embedding for f in feedbacks]
    texts = [f.text for f in feedbacks]
    
    # Run clustering
    clustering_service = get_clustering_service()
    result = clustering_service.cluster_feedback(
        embeddings=embeddings,
        texts=texts,
        n_clusters=n_clusters
    )
    
    # Update feedback with cluster assignments
    if result.get("labels"):
        for i, feedback in enumerate(feedbacks):
            cluster_id = int(result["labels"][i])  # Convert numpy.int64 to Python int
            # Store cluster ID in topics field for now
            # (We could add a dedicated cluster_id field later)
            if feedback.topics is None:
                feedback.topics = []
            feedback.topics = [f"cluster_{cluster_id}"]
        
        await db.commit()
    
    # Convert numpy types to Python types for JSON serialization
    return {
        "success": True,
        "items_clustered": len(feedbacks),
        "clusters_created": int(result.get("n_clusters", 0)),
        "clusters": result.get("clusters", [])
    }


@router.get("/info", response_model=Dict[str, Any])
async def get_clustering_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current clustering information
    """
    # Get all analyzed feedback
    query = select(Feedback).where(
        Feedback.tenant_id == current_user.get("tenant_id"),
        Feedback.analyzed_at.isnot(None)
    )
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    # Count feedback per cluster
    cluster_counts = {}
    for feedback in feedbacks:
        if feedback.topics:
            for topic in feedback.topics:
                if topic.startswith("cluster_"):
                    cluster_counts[topic] = cluster_counts.get(topic, 0) + 1
    
    return {
        "total_feedback": len(feedbacks),
        "clustered_feedback": sum(cluster_counts.values()),
        "clusters": cluster_counts
    }


@router.get("/similar/{feedback_id}", response_model=List[Dict[str, Any]])
async def find_similar_feedback(
    feedback_id: str,
    top_k: int = 5,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar feedback items
    """
    # Get the target feedback
    query = select(Feedback).where(
        Feedback.id == feedback_id,
        Feedback.tenant_id == current_user.get("tenant_id")
    )
    result = await db.execute(query)
    target_feedback = result.scalar_one_or_none()
    
    if not target_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    if not target_feedback.embedding:
        raise HTTPException(
            status_code=400,
            detail="Target feedback has not been analyzed yet"
        )
    
    # Get all other analyzed feedback
    query = select(Feedback).where(
        Feedback.tenant_id == current_user.get("tenant_id"),
        Feedback.analyzed_at.isnot(None),
        Feedback.embedding.isnot(None),
        Feedback.id != feedback_id
    )
    result = await db.execute(query)
    all_feedbacks = result.scalars().all()
    
    if not all_feedbacks:
        return []
    
    # Find similar items
    clustering_service = get_clustering_service()
    embeddings = [f.embedding for f in all_feedbacks]
    similar_indices = clustering_service.find_similar_feedback(
        query_embedding=target_feedback.embedding,
        all_embeddings=embeddings,
        top_k=min(top_k, len(all_feedbacks))
    )
    
    # Build response
    similar_items = []
    for idx, similarity in similar_indices:
        feedback = all_feedbacks[idx]
        similar_items.append({
            "id": str(feedback.id),
            "text": feedback.text,
            "sentiment": feedback.sentiment,
            "similarity": similarity,
            "customer_name": feedback.customer_name
        })
    
    return similar_items
