"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Feedback Analyzer"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # AI/ML API Keys (Optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Sentiment Models
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["csv", "json", "xlsx", "xls", "txt"]
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Analytics
    MIN_CLUSTER_SIZE: int = 5
    MAX_CLUSTERS: int = 20
    SENTIMENT_THRESHOLD: float = 0.6
    URGENCY_HIGH_THRESHOLD: int = 7
    URGENCY_MEDIUM_THRESHOLD: int = 4
    
    # Multi-tenant
    ENABLE_MULTI_TENANT: bool = True
    DEFAULT_TENANT: str = "default"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    # Third-party integrations
    ZENDESK_SUBDOMAIN: Optional[str] = None
    ZENDESK_EMAIL: Optional[str] = None
    ZENDESK_API_TOKEN: Optional[str] = None
    
    INTERCOM_ACCESS_TOKEN: Optional[str] = None
    INTERCOM_APP_ID: Optional[str] = None
    
    FRESHDESK_DOMAIN: Optional[str] = None
    FRESHDESK_API_KEY: Optional[str] = None
    
    HUBSPOT_API_KEY: Optional[str] = None
    HUBSPOT_PORTAL_ID: Optional[str] = None
    
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    
    TEAMS_WEBHOOK_URL: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@feedbackanalyzer.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
