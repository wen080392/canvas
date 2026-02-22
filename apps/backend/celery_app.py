"""
Celery App Configuration for CloudGuardian
"""

from celery import Celery
from celery.schedules import crontab
import os

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "cloudguardian",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    'drift-check-hourly': {
        'task': 'tasks.drift_check.check_all_projects_drift',
        'schedule': crontab(minute=0),  # Every hour
    },
}
