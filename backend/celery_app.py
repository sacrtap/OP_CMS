# OP_CMS Celery Configuration
# Story 7.5: Celery Async Tasks Integration

from celery import Celery
from celery.schedules import crontab
import os

# Celery configuration
celery_app = Celery(
    'op_cms',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Load configuration from environment
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Task routes
    task_routes={
        'backend.tasks.import_customers': {'queue': 'import'},
        'backend.tasks.export_customers': {'queue': 'export'},
        'backend.tasks.send_email': {'queue': 'email'},
    },
    
    # Scheduled tasks
    beat_schedule={
        'daily-backup': {
            'task': 'backend.tasks.daily_backup',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
        'cleanup-old-tasks': {
            'task': 'backend.tasks.cleanup_old_tasks',
            'schedule': crontab(hour=3, minute=0, day_of_week=0),  # 3 AM every Sunday
        },
    },
)

# Auto-discover tasks in installed apps
celery_app.autodiscover_tasks(['backend.tasks'])
