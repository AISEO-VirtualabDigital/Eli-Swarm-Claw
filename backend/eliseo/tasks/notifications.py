"""Celery tasks for notifications and webhooks."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import hashlib
import hmac

import httpx

from eliseo.celery_config import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_webhook_task(
    self,
    webhook_id: str,
    target_url: str,
    event_type: str,
    payload: Dict[str, Any],
    secret: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Send webhook notification to external URL."""
    
    try:
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "X-Event-Type": event_type,
            "X-Webhook-ID": webhook_id,
            "X-Timestamp": datetime.utcnow().isoformat(),
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add signature if secret provided
        if secret:
            payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
            signature = hmac.new(
                secret.encode("utf-8"),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()
            request_headers["X-Signature"] = f"sha256={signature}"
        
        # Send webhook
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                target_url,
                json=payload,
                headers=request_headers,
            )
            
            if response.status_code >= 500:
                # Server error, retry
                raise Exception(f"Server error: {response.status_code}")
            
            return {
                "webhook_id": webhook_id,
                "status": "sent" if response.status_code < 400 else "failed",
                "http_status": response.status_code,
                "response_body": response.text[:1000],  # Limit response size
                "sent_at": datetime.utcnow().isoformat(),
            }
            
    except httpx.RequestError as exc:
        # Network error, retry
        retry_in = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_in)
    except Exception as exc:
        # Other errors
        retry_in = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_in)


@celery_app.task(bind=True, max_retries=3)
def send_email_notification_task(
    self,
    user_id: str,
    email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    notification_type: str = "generation_complete",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send email notification to user."""
    
    # Placeholder for email service integration
    # In production, integrate with SendGrid, AWS SES, etc.
    
    try:
        # Log notification (replace with actual email sending)
        print(f"Email notification to {email}: {subject}")
        
        return {
            "user_id": user_id,
            "email": email,
            "notification_type": notification_type,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as exc:
        retry_in = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_in)


@celery_app.task
def send_generation_complete_notification(
    job_id: str,
    user_id: str,
    email: str,
    asset_urls: List[str],
    generation_type: str = "image",
) -> Dict[str, Any]:
    """Send notification when generation is complete."""
    
    # Send in-app notification (placeholder)
    # In production, save to database
    
    # Send email notification
    subject = f"Your {generation_type} generation is complete!"
    body = f"""
Your {generation_type} has been generated successfully.

Job ID: {job_id}
Assets: {', '.join(asset_urls)}

Thank you for using Eli Claw!
    """
    
    email_result = send_email_notification_task.delay(
        user_id=user_id,
        email=email,
        subject=subject,
        body=body,
        notification_type="generation_complete",
        metadata={"job_id": job_id, "asset_urls": asset_urls},
    )
    
    return {
        "job_id": job_id,
        "email_sent": True,
        "email_task_id": email_result.id,
    }


@celery_app.task
def send_batch_complete_notification(
    batch_id: str,
    user_id: str,
    email: str,
    total_items: int,
    completed_items: int,
    failed_items: int,
) -> Dict[str, Any]:
    """Send notification when batch processing is complete."""
    
    subject = f"Batch generation complete: {completed_items}/{total_items} succeeded"
    body = f"""
Your batch generation has completed.

Batch ID: {batch_id}
Total Items: {total_items}
Completed: {completed_items}
Failed: {failed_items}

Log in to view your generated assets.
    """
    
    email_result = send_email_notification_task.delay(
        user_id=user_id,
        email=email,
        subject=subject,
        body=body,
        notification_type="batch_complete",
        metadata={
            "batch_id": batch_id,
            "total_items": total_items,
            "completed_items": completed_items,
            "failed_items": failed_items,
        },
    )
    
    return {
        "batch_id": batch_id,
        "email_sent": True,
        "email_task_id": email_result.id,
    }


@celery_app.task
def cleanup_old_notifications_task(days_old: int = 30) -> Dict[str, Any]:
    """Clean up old notifications from database."""
    # Placeholder for cleanup logic
    return {
        "status": "completed",
        "days_old": days_old,
        "cleaned_count": 0,  # Would query database in production
    }
