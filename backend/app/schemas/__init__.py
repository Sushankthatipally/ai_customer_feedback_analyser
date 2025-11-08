"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# Enums
class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    
    # Aliases for frontend compatibility
    name: Optional[str] = Field(None, alias="name")
    company: Optional[str] = Field(None, alias="company")


class UserResponse(UserBase):
    id: UUID
    tenant_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    requested_role: Optional[UserRole] = None
    role_approved: bool = True
    is_super_admin: bool = False
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


# Feedback Schemas
class FeedbackBase(BaseModel):
    text: str = Field(..., min_length=1)
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    source: Optional[str] = "manual"
    channel: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    metadata: Optional[Dict[str, Any]] = {}


class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    main_category: Optional[str] = None
    sub_categories: Optional[List[str]] = None


class FeedbackAnalysisResult(BaseModel):
    sentiment: SentimentEnum
    sentiment_score: float
    emotion: str
    emotion_scores: Dict[str, float]
    urgency_level: UrgencyLevel
    urgency_score: int
    main_category: Optional[str]
    topics: List[str]
    keywords: List[str]
    is_feature_request: bool
    is_bug_report: bool
    priority_score: float


class FeedbackResponse(FeedbackBase):
    id: UUID
    tenant_id: UUID
    sentiment: Optional[SentimentEnum]
    sentiment_score: Optional[float]
    emotion: Optional[str]
    urgency_level: Optional[UrgencyLevel]
    urgency_score: Optional[int]
    main_category: Optional[str]
    sub_categories: Optional[List[str]]
    topics: Optional[List[str]]
    keywords: Optional[List[str]]
    priority_score: Optional[float]
    status: str
    created_at: datetime
    analyzed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        populate_by_name = True


# Batch Upload Schema
class BatchUploadResponse(BaseModel):
    job_id: str
    total_items: int
    status: str
    message: str


# Analytics Schemas
class SentimentTrend(BaseModel):
    date: str
    positive: int
    negative: int
    neutral: int
    avg_score: float


class TopicDistribution(BaseModel):
    topic: str
    count: int
    percentage: float
    avg_sentiment: float


class DashboardStats(BaseModel):
    total_feedback: int
    avg_sentiment: float
    sentiment_distribution: Dict[str, int]
    urgency_distribution: Dict[str, int]
    top_topics: List[TopicDistribution]
    sentiment_trend: List[SentimentTrend]
    feature_requests: int
    bug_reports: int


# Cluster Schemas
class ClusterResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    size: int
    avg_sentiment: float
    top_keywords: List[str]
    representative_texts: List[str]
    
    class Config:
        from_attributes = True


# Annotation Schemas
class AnnotationCreate(BaseModel):
    feedback_id: UUID
    comment: Optional[str] = None
    tags: Optional[List[str]] = []
    corrected_category: Optional[str] = None
    is_important: bool = False


class AnnotationResponse(AnnotationCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Integration Schemas
class IntegrationCreate(BaseModel):
    type: str
    name: str
    config: Dict[str, Any]


class IntegrationResponse(BaseModel):
    id: UUID
    type: str
    name: str
    is_active: bool
    last_sync_at: Optional[datetime]
    sync_status: Optional[str]
    
    class Config:
        from_attributes = True


# Report Schemas
class ReportCreate(BaseModel):
    title: str
    report_type: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ReportResponse(ReportCreate):
    id: UUID
    content: Dict[str, Any]
    insights: Dict[str, Any]
    action_items: List[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Insights Schemas
class AIInsight(BaseModel):
    summary: str
    key_findings: List[str]
    action_items: List[Dict[str, str]]
    sentiment_analysis: Dict[str, Any]
    risk_alerts: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]


class ExecutiveSummary(BaseModel):
    period: str
    total_feedback: int
    sentiment_overview: str
    top_issues: List[str]
    top_requests: List[str]
    churn_risk_indicators: List[str]
    recommendations: List[str]
