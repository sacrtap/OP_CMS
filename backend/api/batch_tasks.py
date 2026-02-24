# OP_CMS Batch Tasks API
# Story 6.4: Batch Processing

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Forbidden
import logging

from backend.services.batch_processing_service import batch_service, BatchTaskStatus
from backend.utils.jwt import require_auth

logger = logging.getLogger(__name__)

batch_tasks_bp = Blueprint('batch_tasks', url_prefix='/batch-tasks')


@batch_tasks_bp.route('', methods=['GET'])
@require_auth
async def list_batch_tasks(req: request.Request):
    """
    List batch tasks
    
    Query Parameters:
    - status: Filter by status (pending, processing, completed, failed, cancelled)
    - limit: Limit results (default: 50)
    
    Returns:
    {
        "success": true,
        "data": {
            "tasks": [...],
            "total": 10
        }
    }
    """
    try:
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Parse query parameters
        status = req.args.get('status', '')
        limit = int(req.args.get('limit', 50))
        
        # Get tasks
        tasks = batch_service.list_tasks(user_id=user_id, status=status if status else None, limit=limit)
        
        return json({
            'success': True,
            'data': {
                'tasks': [task.to_dict() for task in tasks],
                'total': len(tasks)
            },
            'message': 'Tasks retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to list batch tasks: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@batch_tasks_bp.route('/<task_id>', methods=['GET'])
@require_auth
async def get_batch_task(req: request.Request, task_id: str):
    """
    Get batch task by ID
    
    Returns:
    {
        "success": true,
        "data": {
            "task": {...}
        }
    }
    """
    try:
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Get task
        task = batch_service.get_task(task_id)
        
        if not task:
            raise NotFound("Task not found")
        
        # Check permissions
        if task.user_id != user_id:
            raise Forbidden("You don't have permission to view this task")
        
        return json({
            'success': True,
            'data': {
                'task': task.to_dict()
            },
            'message': 'Task retrieved successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get batch task: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@batch_tasks_bp.route('/<task_id>', methods=['DELETE'])
@require_auth
async def cancel_batch_task(req: request.Request, task_id: str):
    """
    Cancel batch task
    
    Returns:
    {
        "success": true,
        "message": "Task cancelled successfully"
    }
    """
    try:
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Cancel task
        success = batch_service.cancel_task(task_id, user_id)
        
        if not success:
            task = batch_service.get_task(task_id)
            if not task:
                raise NotFound("Task not found")
            else:
                return json({
                    'success': False,
                    'error': 'Cannot cancel task',
                    'message': 'Task cannot be cancelled (already completed, failed, or cancelled)'
                }, status=400)
        
        return json({
            'success': True,
            'message': 'Task cancelled successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel batch task: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@batch_tasks_bp.route('/stats', methods=['GET'])
@require_auth
async def get_batch_task_stats(req: request.Request):
    """
    Get batch task statistics
    
    Returns:
    {
        "success": true,
        "data": {
            "total": 100,
            "by_status": {
                "pending": 5,
                "processing": 2,
                "completed": 90,
                "failed": 2,
                "cancelled": 1
            }
        }
    }
    """
    try:
        # Get current user
        current_user = getattr(req, 'current_user', {})
        user_id = current_user.get('user_id')
        
        if not user_id:
            return json({
                'success': False,
                'error': 'Authentication required',
                'message': 'User not authenticated'
            }, status=401)
        
        # Get all tasks for user
        all_tasks = batch_service.list_tasks(user_id=user_id, limit=1000)
        
        # Calculate statistics
        stats = {
            'total': len(all_tasks),
            'by_status': {
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'cancelled': 0
            }
        }
        
        for task in all_tasks:
            if task.status in stats['by_status']:
                stats['by_status'][task.status] += 1
        
        return json({
            'success': True,
            'data': stats,
            'message': 'Statistics retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get batch task statistics: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
