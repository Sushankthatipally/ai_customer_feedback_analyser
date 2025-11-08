"""
Authentication Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models import User, Tenant, UserRole
from app.schemas import UserCreate, UserResponse, Token
from app.core.config import settings
import uuid

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Assign to default tenant (all users in same organization)
    # Check if default tenant exists, create if not
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.slug == "default")
    )
    tenant = tenant_result.scalar_one_or_none()
    
    if not tenant:
        # Create default tenant for all users
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Feedback Analyzer Organization",
            slug="default",
            settings={},
            is_active=True
        )
        db.add(tenant)
        await db.flush()  # Flush to get the tenant ID
    
    # Create new user
    # If user requests admin role, set it as pending approval
    # Convert role string to UserRole enum (handle both lowercase and uppercase)
    role_str = user_data.role.lower() if isinstance(user_data.role, str) else str(user_data.role).lower()
    
    if role_str == "admin":
        assigned_role = UserRole.VIEWER  # Assign viewer role temporarily
        requested_role = UserRole.ADMIN
        role_approved = False
    elif role_str == "analyst":
        assigned_role = UserRole.ANALYST
        requested_role = None
        role_approved = True
    else:  # viewer or any other value
        assigned_role = UserRole.VIEWER
        requested_role = None
        role_approved = True
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=assigned_role,
        requested_role=requested_role,
        role_approved=role_approved,
        tenant_id=tenant.id  # Assign tenant_id
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    
    # Find user
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id), 
            "email": user.email, 
            "role": user.role.value,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None
        }
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Verify user still exists and is active
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
