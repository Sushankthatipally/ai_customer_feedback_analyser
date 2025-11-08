"""
User Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, verify_password, get_password_hash
from app.models import User
from app.schemas import UserResponse, UserUpdate
from pydantic import BaseModel

router = APIRouter()


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    result = await db.execute(
        select(User).where(User.id == current_user.get("sub"))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all users (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    
    return users


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    # Get current user from database
    result = await db.execute(
        select(User).where(User.id == current_user.get("sub"))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.add(user)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user information"""
    result = await db.execute(
        select(User).where(User.id == current_user.get("sub"))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Map 'name' to 'full_name' if provided
    if 'name' in update_data:
        update_data['full_name'] = update_data.pop('name')
    
    # Remove 'company' as it's not in User model (could be added to settings)
    if 'company' in update_data:
        update_data.pop('company')
    
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user
