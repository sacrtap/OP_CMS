# OP_CMS Batch Processing Service
# Story 6.4: Batch Processing

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class BatchTaskStatus:
    """Task status constants"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class BatchTask:
    """Batch task representation"""
    
    def __init__(self, task_type: str, user_id: int, total_records: int = 0):
        self.id = str(uuid.uuid4())
        self.task_type = task_type  # import, export
        self.user_id = user_id
        self.status = BatchTaskStatus.PENDING
        self.progress = 0  # 0-100
        self.total_records = total_records
        self.processed_records = 0
        self.successful_records = 0
        self.failed_records = 0
        self.result_url = None
        self.error_message = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.cancelled = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'task_type': self.task_type,
            'user_id': self.user_id,
            'status': self.status,
            'progress': self.progress,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'successful_records': self.successful_records,
            'failed_records': self.failed_records,
            'result_url': self.result_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_time_remaining': self._estimate_time_remaining()
        }
    
    def _estimate_time_remaining(self) -> Optional[int]:
        """Estimate time remaining in seconds"""
        if not self.started_at or self.progress == 0:
            return None
        
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        if self.progress > 0:
            total_estimated = elapsed / (self.progress / 100)
            remaining = total_estimated - elapsed
            return max(0, int(remaining))
        return None
    
    def update_progress(self, processed: int, successful: int = None, failed: int = None):
        """Update task progress"""
        self.processed_records = processed
        if successful is not None:
            self.successful_records = successful
        if failed is not None:
            self.failed_records = failed
        
        if self.total_records > 0:
            self.progress = int((self.processed_records / self.total_records) * 100)
        else:
            self.progress = min(100, self.progress)
    
    def start(self):
        """Mark task as started"""
        self.status = BatchTaskStatus.PROCESSING
        self.started_at = datetime.utcnow()
    
    def complete(self, result_url: str = None):
        """Mark task as completed"""
        self.status = BatchTaskStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.utcnow()
        self.result_url = result_url
    
    def fail(self, error_message: str):
        """Mark task as failed"""
        self.status = BatchTaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def cancel(self):
        """Mark task as cancelled"""
        self.status = BatchTaskStatus.CANCELLED
        self.cancelled = True
        self.completed_at = datetime.utcnow()


class BatchProcessingService:
    """Service for batch processing operations"""
    
    def __init__(self):
        self.tasks: Dict[str, BatchTask] = {}
    
    def create_task(self, task_type: str, user_id: int, total_records: int = 0) -> BatchTask:
        """Create a new batch task"""
        task = BatchTask(task_type, user_id, total_records)
        self.tasks[task.id] = task
        logger.info(f"Created batch task {task.id} for user {user_id}, type: {task_type}")
        return task
    
    def get_task(self, task_id: str) -> Optional[BatchTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, user_id: int = None, status: str = None, limit: int = 50) -> List[BatchTask]:
        """List tasks with optional filtering"""
        tasks = list(self.tasks.values())
        
        # Filter by user_id
        if user_id:
            tasks = [t for t in tasks if t.user_id == user_id]
        
        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Limit results
        return tasks[:limit]
    
    def cancel_task(self, task_id: str, user_id: int) -> bool:
        """Cancel a task"""
        task = self.get_task(task_id)
        
        if not task:
            return False
        
        if task.user_id != user_id:
            return False
        
        if task.status in [BatchTaskStatus.COMPLETED, BatchTaskStatus.FAILED, BatchTaskStatus.CANCELLED]:
            return False
        
        task.cancel()
        logger.info(f"Cancelled batch task {task_id}")
        return True
    
    def process_batch(
        self,
        task: BatchTask,
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Process items in batches with progress tracking
        
        Args:
            task: BatchTask to update
            items: List of items to process
            process_func: Function to process each item
            batch_size: Number of items per batch
            
        Returns:
            Processing results
        """
        task.start()
        
        total = len(items)
        successful = 0
        failed = 0
        errors = []
        
        try:
            for i in range(0, total, batch_size):
                if task.cancelled:
                    logger.info(f"Batch processing cancelled for task {task.id}")
                    break
                
                batch = items[i:i + batch_size]
                
                # Process batch
                for item in batch:
                    try:
                        result = process_func(item)
                        if result:
                            successful += 1
                        else:
                            failed += 1
                            errors.append({
                                'item': item,
                                'error': 'Processing failed'
                            })
                    except Exception as e:
                        failed += 1
                        errors.append({
                            'item': item,
                            'error': str(e)
                        })
                
                # Update progress
                processed = min(i + batch_size, total)
                task.update_progress(processed, successful, failed)
                logger.info(f"Batch task {task.id} progress: {task.progress}%")
            
            # Complete task
            if task.cancelled:
                task.cancel()
            else:
                task.complete()
            
            return {
                'total': total,
                'successful': successful,
                'failed': failed,
                'errors': errors[:100]  # Limit errors
            }
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            task.fail(str(e))
            raise
    
    def export_batch(
        self,
        task: BatchTask,
        query_func: Callable,
        export_func: Callable,
        batch_size: int = 1000
    ) -> str:
        """
        Export data in batches with streaming
        
        Args:
            task: BatchTask to update
            query_func: Function to get total count
            export_func: Function to export a batch
            batch_size: Number of records per batch
            
        Returns:
            Result URL
        """
        task.start()
        
        try:
            # Get total count
            total = query_func()
            task.total_records = total
            
            # Export in batches
            offset = 0
            exported = 0
            
            while offset < total:
                if task.cancelled:
                    break
                
                # Export batch
                batch_result = export_func(offset=offset, limit=batch_size)
                exported += batch_result.get('count', 0)
                offset += batch_size
                
                # Update progress
                task.update_progress(exported)
                logger.info(f"Export task {task.id} progress: {task.progress}%")
            
            # Complete task
            if task.cancelled:
                task.cancel()
            else:
                result_url = f"/downloads/export_{task.id}.xlsx"
                task.complete(result_url)
                return result_url
            
        except Exception as e:
            logger.error(f"Batch export failed: {str(e)}")
            task.fail(str(e))
            raise


# Global batch processing service instance
batch_service = BatchProcessingService()
