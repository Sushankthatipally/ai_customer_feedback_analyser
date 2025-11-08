"""
Admin Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.models import User, UserRole
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ApproveRoleRequest(BaseModel):
    user_id: str
    approved: bool


class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    role: str
    requested_role: str | None
    role_approved: bool
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/users", response_model=List[UserInfo])
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only, super admin sees all tenants)"""
    
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all users"
        )
    
    # Get current user to check if super admin
    user_query = select(User).where(User.id == current_user.get("sub"))
    user_result = await db.execute(user_query)
    current_user_obj = user_result.scalar_one_or_none()
    
    # Build query based on super admin status
    if current_user_obj and current_user_obj.is_super_admin:
        # Super admin sees all users across all tenants
        query = select(User).order_by(User.created_at.desc())
    else:
        # Regular admin sees only users in their tenant
        query = select(User).where(
            User.tenant_id == current_user.get("tenant_id")
        ).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "requested_role": user.requested_role.value if user.requested_role else None,
            "role_approved": user.role_approved,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


@router.get("/pending-requests", response_model=List[UserInfo])
async def get_pending_role_requests(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending admin role requests (admin only, super admin sees all tenants)"""
    
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view pending requests"
        )
    
    # Get current user to check if super admin
    user_query = select(User).where(User.id == current_user.get("sub"))
    user_result = await db.execute(user_query)
    current_user_obj = user_result.scalar_one_or_none()
    
    # Build query based on super admin status
    if current_user_obj and current_user_obj.is_super_admin:
        # Super admin sees all pending requests across all tenants
        query = select(User).where(
            User.role_approved == False,
            User.requested_role.isnot(None)
        ).order_by(User.created_at.desc())
    else:
        # Regular admin sees only pending requests in their tenant
        query = select(User).where(
            User.tenant_id == current_user.get("tenant_id"),
            User.role_approved == False,
            User.requested_role.isnot(None)
        ).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "requested_role": user.requested_role.value if user.requested_role else None,
            "role_approved": user.role_approved,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


@router.post("/approve-role")
async def approve_role_request(
    request: ApproveRoleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject a role request (admin only)"""
    
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve role requests"
        )
    
    # Get the user
    query = select(User).where(User.id == request.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.approved:
        # Approve: assign the requested role
        if user.requested_role:
            user.role = user.requested_role
        user.role_approved = True
        user.requested_role = None
        message = f"User {user.username} has been granted {user.role.value} role"
    else:
        # Reject: keep current role and clear request
        user.role_approved = True
        user.requested_role = None
        message = f"Role request for {user.username} has been rejected"
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "success": True,
        "message": message,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "role_approved": user.role_approved
        }
    }


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a user account (admin only)"""
    
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update user status"
        )
    
    # Get the user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = is_active
    await db.commit()
    
    return {
        "success": True,
        "message": f"User {user.username} has been {'activated' if is_active else 'deactivated'}",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "is_active": user.is_active
        }
    }
