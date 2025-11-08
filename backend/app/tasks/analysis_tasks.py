"""
Celery Tasks for Background Processing
"""

from celery import Celery
from datetime import datetime
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import Feedback
from app.services.ai_analyzer import get_ai_analyzer
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "feedback_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="analyze_feedback")
def analyze_feedback_task(feedback_id: str):
    """
    Background task to analyze feedback using AI/ML models
    """
    import asyncio
    
    async def _analyze():
        async with AsyncSessionLocal() as session:
            try:
                # Get feedback
                result = await session.execute(
                    select(Feedback).where(Feedback.id == feedback_id)
                )
                feedback = result.scalar_one_or_none()
                
                if not feedback:
                    logger.error(f"Feedback {feedback_id} not found")
                    return
                
                # Get AI analyzer
                analyzer = get_ai_analyzer()
                
                # Analyze feedback
                analysis = analyzer.analyze_feedback(feedback.text)
                
                # Update feedback with analysis results
                feedback.sentiment = analysis.get("sentiment")
                feedback.sentiment_score = analysis.get("sentiment_score")
                feedback.emotion = analysis.get("emotion")
                feedback.emotion_scores = analysis.get("emotion_scores")
                feedback.urgency_score = analysis.get("urgency_score")
                feedback.urgency_level = analysis.get("urgency_level")
                feedback.keywords = analysis.get("keywords")
                feedback.embedding = analysis.get("embedding")
                feedback.is_feature_request = analysis.get("is_feature_request")
                feedback.is_bug_report = analysis.get("is_bug_report")
                feedback.competitor_names = analysis.get("competitor_mentions")
                feedback.priority_score = analysis.get("priority_score")
                feedback.analyzed_at = datetime.utcnow()
                
                await session.commit()
                
                logger.info(f"Successfully analyzed feedback {feedback_id}")
                
            except Exception as e:
                logger.error(f"Error analyzing feedback {feedback_id}: {str(e)}")
                await session.rollback()
    
    # Get or create event loop for async operations
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run async function
    loop.run_until_complete(_analyze())


@celery_app.task(name="sync_integration")
def sync_integration_task(integration_id: str, integration_type: str):
    """
    Background task to sync data from third-party integrations
    """
    logger.info(f"Syncing integration {integration_id} ({integration_type})")
    # Implementation for different integration types
    pass


@celery_app.task(name="generate_report")
def generate_report_task(report_id: str):
    """
    Background task to generate analytics reports
    """
    logger.info(f"Generating report {report_id}")
    # Implementation for report generation
    pass
