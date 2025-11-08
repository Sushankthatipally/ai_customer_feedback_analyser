"""
API Router Configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    feedback,
    analytics,
    integrations,
    reports,
    users,
    clustering,
    admin
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(clustering.router, prefix="/clustering", tags=["Clustering"])
