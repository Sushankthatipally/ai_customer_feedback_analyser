"""
Celery tasks package
"""

from app.tasks.analysis_tasks import celery_app, analyze_feedback_task

__all__ = ['celery_app', 'analyze_feedback_task']
