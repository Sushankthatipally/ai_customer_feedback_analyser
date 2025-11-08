"""
Analytics and Dashboard Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Feedback
from app.schemas import DashboardStats, SentimentTrend, TopicDistribution

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total feedback count
    total_result = await db.execute(
        select(func.count(Feedback.id)).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.created_at >= start_date
            )
        )
    )
    total_feedback = total_result.scalar()
    
    # Average sentiment
    avg_sentiment_result = await db.execute(
        select(func.avg(Feedback.sentiment_score)).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.created_at >= start_date
            )
        )
    )
    avg_sentiment = avg_sentiment_result.scalar() or 0.0
    
    # Sentiment distribution
    sentiment_dist_result = await db.execute(
        select(
            Feedback.sentiment,
            func.count(Feedback.id)
        ).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.created_at >= start_date
            )
        ).group_by(Feedback.sentiment)
    )
    
    sentiment_distribution = {
        row[0]: row[1] for row in sentiment_dist_result.all() if row[0]
    }
    
    # Urgency distribution
    urgency_dist_result = await db.execute(
        select(
            Feedback.urgency_level,
            func.count(Feedback.id)
        ).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.created_at >= start_date
            )
        ).group_by(Feedback.urgency_level)
    )
    
    urgency_distribution = {
        row[0]: row[1] for row in urgency_dist_result.all() if row[0]
    }
    
    # Feature requests and bug reports
    feature_requests_result = await db.execute(
        select(func.count(Feedback.id)).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.is_feature_request == True,
                Feedback.created_at >= start_date
            )
        )
    )
    feature_requests = feature_requests_result.scalar()
    
    bug_reports_result = await db.execute(
        select(func.count(Feedback.id)).where(
            and_(
                Feedback.tenant_id == current_user.get("tenant_id"),
                Feedback.is_bug_report == True,
                Feedback.created_at >= start_date
            )
        )
    )
    bug_reports = bug_reports_result.scalar()
    
    # Sentiment trend (last 7 days)
    sentiment_trend = []
    for i in range(7):
        day = end_date - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        sentiment_day_result = await db.execute(
            select(
                Feedback.sentiment,
                func.count(Feedback.id),
                func.avg(Feedback.sentiment_score)
            ).where(
                and_(
                    Feedback.tenant_id == current_user.get("tenant_id"),
                    Feedback.created_at >= day_start,
                    Feedback.created_at < day_end
                )
            ).group_by(Feedback.sentiment)
        )
        
        day_data = {"date": day.strftime("%Y-%m-%d"), "positive": 0, "negative": 0, "neutral": 0, "avg_score": 0.0}
        
        for row in sentiment_day_result.all():
            if row[0]:
                day_data[row[0]] = row[1]
                day_data["avg_score"] = row[2] or 0.0
        
        sentiment_trend.append(day_data)
    
    return {
        "total_feedback": total_feedback,
        "avg_sentiment": float(avg_sentiment),
        "sentiment_distribution": sentiment_distribution,
        "urgency_distribution": urgency_distribution,
        "top_topics": [],  # Implemented separately
        "sentiment_trend": list(reversed(sentiment_trend)),
        "feature_requests": feature_requests,
        "bug_reports": bug_reports
    }


@router.get("/trends/sentiment")
async def get_sentiment_trends(
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed sentiment trends"""
    # Implementation similar to dashboard but more detailed
    return {"status": "trends"}


@router.get("/topics/distribution")
async def get_topic_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get topic distribution statistics"""
    # Implementation for topic analysis
    return {"topics": []}
