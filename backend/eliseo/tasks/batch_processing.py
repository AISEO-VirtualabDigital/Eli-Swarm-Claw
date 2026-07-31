"""Celery tasks for batch processing."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from eliseo.celery_config import celery_app
from eliseo.tasks.media_generation import generate_image_task, generate_video_task


@celery_app.task(bind=True)
def process_batch_task(
    self,
    batch_id: str,
    items: List[Dict[str, Any]],
    generation_type: str = "image",
    provider_type: str = "mock",
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Process a batch of generation requests."""
    
    total_items = len(items)
    completed_items = 0
    failed_items = 0
    results = []
    
    for idx, item in enumerate(items):
        try:
            if generation_type == "image":
                result = generate_image_task.delay(
                    job_id=f"{batch_id}_item_{idx}",
                    prompt=item.get("prompt", ""),
                    provider_type=provider_type,
                    width=item.get("width", 1024),
                    height=item.get("height", 1024),
                    model=item.get("model"),
                    negative_prompt=item.get("negative_prompt"),
                    steps=item.get("steps", 30),
                    guidance_scale=item.get("guidance_scale", 7.5),
                    seed=item.get("seed"),
                    style_preset=item.get("style_preset"),
                    output_format=item.get("output_format", "png"),
                    user_id=user_id,
                    organization_id=organization_id,
                )
                # Wait for result (in production, use webhook instead)
                result_value = result.get(timeout=600)
                
            elif generation_type == "video":
                result = generate_video_task.delay(
                    job_id=f"{batch_id}_item_{idx}",
                    prompt=item.get("prompt", ""),
                    provider_type=provider_type,
                    width=item.get("width", 1024),
                    height=item.get("height", 1024),
                    duration_seconds=item.get("duration_seconds", 5),
                    fps=item.get("fps", 24),
                    model=item.get("model"),
                    negative_prompt=item.get("negative_prompt"),
                    seed=item.get("seed"),
                    output_format=item.get("output_format", "mp4"),
                    user_id=user_id,
                    organization_id=organization_id,
                )
                # Wait for result
                result_value = result.get(timeout=900)
                
            else:
                raise ValueError(f"Unknown generation type: {generation_type}")
            
            results.append({
                "item_index": idx,
                "job_id": f"{batch_id}_item_{idx}",
                "status": "completed",
                "result": result_value,
            })
            completed_items += 1
            
        except Exception as e:
            results.append({
                "item_index": idx,
                "job_id": f"{batch_id}_item_{idx}",
                "status": "failed",
                "error": str(e),
            })
            failed_items += 1
    
    # Determine batch status
    if failed_items == 0:
        batch_status = "completed"
    elif completed_items == 0:
        batch_status = "failed"
    else:
        batch_status = "partially_completed"
    
    return {
        "batch_id": batch_id,
        "status": batch_status,
        "total_items": total_items,
        "completed_items": completed_items,
        "failed_items": failed_items,
        "results": results,
        "completed_at": datetime.utcnow().isoformat(),
    }


@celery_app.task
def retry_failed_batch_items_task(
    batch_id: str,
    failed_item_indices: List[int],
    original_items: List[Dict[str, Any]],
    generation_type: str = "image",
    provider_type: str = "mock",
) -> Dict[str, Any]:
    """Retry failed items in a batch."""
    
    items_to_retry = [original_items[idx] for idx in failed_item_indices if idx < len(original_items)]
    
    if not items_to_retry:
        return {
            "batch_id": batch_id,
            "status": "no_items_to_retry",
            "retried_count": 0,
        }
    
    # Process retry
    retry_result = process_batch_task.delay(
        batch_id=f"{batch_id}_retry",
        items=items_to_retry,
        generation_type=generation_type,
        provider_type=provider_type,
    )
    
    return {
        "batch_id": batch_id,
        "status": "retry_initiated",
        "retry_batch_id": f"{batch_id}_retry",
        "retried_count": len(items_to_retry),
    }
