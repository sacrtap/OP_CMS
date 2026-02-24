# OP_CMS Backup Management API
# Story 7.3: Data Backup & Recovery

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Forbidden
import logging

from backend.services.backup_service import backup_service
from backend.utils.jwt import require_auth, require_role

logger = logging.getLogger(__name__)

backups_bp = Blueprint('backups', url_prefix='/backups')


@backups_bp.route('', methods=['GET'])
@require_auth
@require_role('admin')
async def list_backups(req: request.Request):
    """
    List all backups
    
    Returns:
    {
        "success": true,
        "data": {
            "backups": [...],
            "total": 10
        }
    }
    """
    try:
        backups = backup_service.list_backups()
        
        return json({
            'success': True,
            'data': {
                'backups': backups,
                'total': len(backups)
            },
            'message': 'Backups retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@backups_bp.route('', methods=['POST'])
@require_auth
@require_role('admin')
async def create_backup(req: request.Request):
    """
    Create new backup
    
    Request Body:
    {
        "type": "full",  // full, incremental
        "description": "Manual backup"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "backup": {...}
        }
    }
    """
    try:
        data = req.json or {}
        backup_type = data.get('type', 'full')
        description = data.get('description', '')
        
        if backup_type not in ['full', 'incremental']:
            return json({
                'success': False,
                'error': 'Invalid backup type',
                'message': f'Invalid backup type: {backup_type}. Valid types: full, incremental'
            }, status=400)
        
        # Create backup
        backup_info = backup_service.create_backup(backup_type=backup_type, description=description)
        
        return json({
            'success': True,
            'data': {
                'backup': backup_info
            },
            'message': 'Backup created successfully'
        }, status=201)
        
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return json({
            'success': False,
            'error': 'Backup failed',
            'message': str(e)
        }, status=500)


@backups_bp.route('/<backup_filename:path>', methods=['DELETE'])
@require_auth
@require_role('admin')
async def delete_backup(req: request.Request, backup_filename: str):
    """
    Delete backup file
    
    Returns:
    {
        "success": true,
        "message": "Backup deleted successfully"
    }
    """
    try:
        success = backup_service.delete_backup(backup_filename)
        
        if not success:
            raise NotFound("Backup not found")
        
        return json({
            'success': True,
            'message': 'Backup deleted successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to delete backup: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@backups_bp.route('/<backup_filename:path>/restore', methods=['POST'])
@require_auth
@require_role('admin')
async def restore_backup(req: request.Request, backup_filename: str):
    """
    Restore database from backup
    
    Request Body:
    {
        "confirm": true  // Must be true to confirm restore
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "restore": {...}
        }
    }
    """
    try:
        data = req.json or {}
        
        if not data.get('confirm', False):
            return json({
                'success': False,
                'error': 'Confirmation required',
                'message': 'Restore will overwrite current database. Set confirm=true to proceed.'
            }, status=400)
        
        # Find backup path
        backups = backup_service.list_backups()
        backup = next((b for b in backups if b['filename'] == backup_filename), None)
        
        if not backup:
            raise NotFound("Backup not found")
        
        # Restore backup
        restore_info = backup_service.restore_backup(backup['path'])
        
        return json({
            'success': True,
            'data': {
                'restore': restore_info
            },
            'message': 'Database restored successfully'
        })
        
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to restore backup: {str(e)}")
        return json({
            'success': False,
            'error': 'Restore failed',
            'message': str(e)
        }, status=500)


@backups_bp.route('/config', methods=['GET'])
@require_auth
@require_role('admin')
async def get_backup_config(req: request.Request):
    """
    Get backup configuration
    
    Returns:
    {
        "success": true,
        "data": {
            "config": {
                "auto_backup_enabled": true,
                "backup_frequency": "daily",
                "keep_count": 10,
                "backup_time": "02:00"
            }
        }
    }
    """
    try:
        # Mock configuration (in production, load from system parameters)
        config = {
            'auto_backup_enabled': True,
            'backup_frequency': 'daily',  # daily, weekly, monthly
            'keep_count': 10,
            'backup_time': '02:00',
            'backup_dir': backup_service.backup_dir
        }
        
        return json({
            'success': True,
            'data': {
                'config': config
            },
            'message': 'Backup configuration retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get backup config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@backups_bp.route('/config', methods=['PUT'])
@require_auth
@require_role('admin')
async def update_backup_config(req: request.Request):
    """
    Update backup configuration
    
    Request Body:
    {
        "auto_backup_enabled": true,
        "backup_frequency": "daily",
        "keep_count": 10,
        "backup_time": "02:00"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "config": {...}
        }
    }
    """
    try:
        data = req.json
        
        # Validate configuration
        if 'keep_count' in data:
            if not isinstance(data['keep_count'], int) or data['keep_count'] < 1:
                return json({
                    'success': False,
                    'error': 'Invalid configuration',
                    'message': 'keep_count must be a positive integer'
                }, status=400)
        
        if 'backup_frequency' in data:
            if data['backup_frequency'] not in ['daily', 'weekly', 'monthly']:
                return json({
                    'success': False,
                    'error': 'Invalid configuration',
                    'message': 'backup_frequency must be daily, weekly, or monthly'
                }, status=400)
        
        # In production, save to system parameters
        # For now, just return the configuration
        config = {
            'auto_backup_enabled': data.get('auto_backup_enabled', True),
            'backup_frequency': data.get('backup_frequency', 'daily'),
            'keep_count': data.get('keep_count', 10),
            'backup_time': data.get('backup_time', '02:00'),
            'backup_dir': backup_service.backup_dir
        }
        
        return json({
            'success': True,
            'data': {
                'config': config
            },
            'message': 'Backup configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to update backup config: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@backups_bp.route('/cleanup', methods=['POST'])
@require_auth
@require_role('admin')
async def cleanup_backups(req: request.Request):
    """
    Cleanup old backups
    
    Request Body:
    {
        "keep_count": 10  // Number of backups to keep
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "deleted_count": 5
        }
    }
    """
    try:
        data = req.json or {}
        keep_count = data.get('keep_count', 10)
        
        if not isinstance(keep_count, int) or keep_count < 1:
            return json({
                'success': False,
                'error': 'Invalid keep_count',
                'message': 'keep_count must be a positive integer'
            }, status=400)
        
        # Cleanup old backups
        deleted_count = backup_service.cleanup_old_backups(keep_count=keep_count)
        
        return json({
            'success': True,
            'data': {
                'deleted_count': deleted_count
            },
            'message': f'Cleaned up {deleted_count} old backups'
        })
        
    except Exception as e:
        logger.error(f"Failed to cleanup backups: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
