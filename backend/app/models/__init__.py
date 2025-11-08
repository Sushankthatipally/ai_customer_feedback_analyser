"""
Database Models for Feedback Analyzer
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SentimentEnum(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    requested_role = Column(Enum(UserRole))  # Role user requested (for admin approval)
    role_approved = Column(Boolean, default=True)  # Whether role is approved
    is_super_admin = Column(Boolean, default=False)  # Can manage across all tenants
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    annotations = relationship("Annotation", back_populates="user")


class Tenant(Base):
    """Multi-tenant organization model"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    feedbacks = relationship("Feedback", back_populates="tenant")


class Feedback(Base):
    """Customer feedback model"""
    __tablename__ = "feedbacks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Original data
    customer_id = Column(String(255), index=True)
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    text = Column(Text, nullable=False)
    source = Column(String(50))  # zendesk, intercom, manual, etc.
    source_id = Column(String(255))  # Original ID from source system
    channel = Column(String(50))  # email, chat, survey, etc.
    
    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)
    language = Column(String(10), default="en")
    feedback_metadata = Column(JSON, default={})
    
    # AI Analysis Results
    sentiment = Column(Enum(SentimentEnum))
    sentiment_score = Column(Float)  # -1 to 1
    emotion = Column(String(50))  # joy, anger, sadness, fear, etc.
    emotion_scores = Column(JSON)  # Detailed emotion breakdown
    urgency_level = Column(Enum(UrgencyLevel))
    urgency_score = Column(Integer)  # 1-10
    
    # Categorization
    main_category = Column(String(100))
    sub_categories = Column(ARRAY(String))
    topics = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    
    # Embeddings for similarity search
    embedding = Column(ARRAY(Float))  # Vector embedding
    
    # Additional insights
    is_feature_request = Column(Boolean, default=False)
    is_bug_report = Column(Boolean, default=False)
    is_competitor_mention = Column(Boolean, default=False)
    competitor_names = Column(ARRAY(String))
    
    # Priority & Status
    priority_score = Column(Float)  # AI-calculated priority
    status = Column(String(50), default="new")  # new, reviewed, actioned, closed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    analyzed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="feedbacks")
    annotations = relationship("Annotation", back_populates="feedback")
    clusters = relationship("FeedbackCluster", secondary="feedback_cluster_association", back_populates="feedbacks")


class Category(Base):
    """Custom feedback categories"""
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    keywords = Column(ARRAY(String))
    color = Column(String(7))  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")


class FeedbackCluster(Base):
    """Topic clusters from feedback analysis"""
    __tablename__ = "feedback_clusters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String(255))
    description = Column(Text)
    size = Column(Integer)  # Number of feedback items
    avg_sentiment = Column(Float)
    top_keywords = Column(ARRAY(String))
    representative_texts = Column(ARRAY(Text))  # Sample feedback
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedbacks = relationship("Feedback", secondary="feedback_cluster_association", back_populates="clusters")


class FeedbackClusterAssociation(Base):
    """Many-to-many relationship between feedback and clusters"""
    __tablename__ = "feedback_cluster_association"
    
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("feedbacks.id"), primary_key=True)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("feedback_clusters.id"), primary_key=True)
    similarity_score = Column(Float)


class Annotation(Base):
    """User annotations on feedback"""
    __tablename__ = "annotations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("feedbacks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    comment = Column(Text)
    tags = Column(ARRAY(String))
    corrected_category = Column(String(100))
    is_important = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="annotations")
    user = relationship("User", back_populates="annotations")


class Integration(Base):
    """Third-party integrations configuration"""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    
    type = Column(String(50), nullable=False)  # zendesk, intercom, slack, etc.
    name = Column(String(255))
    config = Column(JSON)  # Encrypted credentials and settings
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime)
    sync_status = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Generated reports and insights"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    
    title = Column(String(255), nullable=False)
    report_type = Column(String(50))  # executive_summary, trend_analysis, etc.
    content = Column(JSON)
    insights = Column(JSON)
    action_items = Column(JSON)
    
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    """Automated alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    
    type = Column(String(50))  # churn_risk, negative_spike, etc.
    severity = Column(String(20))  # low, medium, high
    title = Column(String(255))
    message = Column(Text)
    data = Column(JSON)
    
    is_read = Column(Boolean, default=False)
    is_actioned = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
