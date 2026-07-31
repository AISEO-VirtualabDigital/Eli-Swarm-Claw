"""Celery configuration for Eli Claw background tasks."""

import os
from celery import Celery
from kombu import Exchange, Queue

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Create Celery app
celery_app = Celery(
    "eliseo",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "eliseo.tasks.media_generation",
        "eliseo.tasks.batch_processing",
        "eliseo.tasks.notifications",
    ],
)

# Configure task routing
celery_app.conf.task_routes = {
    "eliseo.tasks.media_generation.generate_image_task": {"queue": "media"},
    "eliseo.tasks.media_generation.generate_video_task": {"queue": "media"},
    "eliseo.tasks.batch_processing.process_batch_task": {"queue": "batch"},
    "eliseo.tasks.notifications.send_notification_task": {"queue": "notifications"},
}

# Configure queues
celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("media", Exchange("media"), routing_key="media"),
    Queue("batch", Exchange("batch"), routing_key="batch"),
    Queue("notifications", Exchange("notifications"), routing_key="notifications"),
)

# Auto-discover tasks
celery_app.autodiscover_tasks()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks if needed."""
    pass
