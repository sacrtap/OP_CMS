# OP_CMS Audit Log API
# Story 5.3: Operation Audit Log

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest
from typing import Optional
import logging
from datetime import datetime, timedelta

from backend.models.database_models import AuditLog, User
from backend.dao.database_dao import DatabaseSessionFactory
from backend.utils.jwt import require_auth, require_role

logger = logging.getLogger(__name__)

audit_logs_bp = Blueprint('audit_logs', url_prefix='/audit-logs')


@audit_logs_bp.route('', methods=['GET'])
@require_auth
@require_role('admin')
async def get_audit_logs(req: request.Request):
    """
    Get audit logs with filtering and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - user_id: Filter by user ID
    - action_type: Filter by action type (create, update, delete, view, export)
    - resource_type: Filter by resource type (customer, pricing, settlement, user)
    - date_from: Filter from date (ISO format)
    - date_to: Filter to date (ISO format)
    - search: Search in action description
    
    Returns:
    {
        "success": true,
        "data": {
            "audit_logs": [...],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
    }
    """
    try:
        # Parse query parameters
        page = max(1, int(req.args.get('page', 1)))
        page_size = min(100, max(1, int(req.args.get('page_size', 20))))
        user_id = req.args.get('user_id', '')
        action_type = req.args.get('action_type', '')
        resource_type = req.args.get('resource_type', '')
        date_from = req.args.get('date_from', '')
        date_to = req.args.get('date_to', '')
        search = req.args.get('search', '')
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query
            query = session.query(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.filter(AuditLog.user_id == int(user_id))
            
            if action_type:
                query = query.filter(AuditLog.action_type == action_type)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from)
                    query = query.filter(AuditLog.created_at >= from_date)
                except:
                    pass
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to)
                    query = query.filter(AuditLog.created_at <= to_date)
                except:
                    pass
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            audit_logs = query.order_by(
                AuditLog.created_at.desc()
            ).offset(offset).limit(page_size).all()
            
            # Convert to response format
            logs_data = []
            for log in audit_logs:
                log_entry = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'username': log.username,
                    'action': log.action,
                    'action_type': log.action_type,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                    'old_value': log.old_value,
                    'new_value': log.new_value
                }
                logs_data.append(log_entry)
            
            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size
            
            return json({
                'success': True,
                'data': {
                    'audit_logs': logs_data,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'filters': {
                        'user_id': user_id,
                        'action_type': action_type,
                        'resource_type': resource_type,
                        'date_from': date_from,
                        'date_to': date_to,
                        'search': search
                    }
                },
                'message': 'Audit logs retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@audit_logs_bp.route('/<log_id:int>', methods=['GET'])
@require_auth
@require_role('admin')
async def get_audit_log_detail(req: request.Request, log_id: int):
    """
    Get audit log detail by ID
    
    Returns:
    {
        "success": true,
        "data": {
            "audit_log": {...}
        }
    }
    """
    try:
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Find audit log
            audit_log = session.query(AuditLog).filter(AuditLog.id == log_id).first()
            
            if not audit_log:
                raise NotFound("Audit log not found")
            
            # Get user info if exists
            user = None
            if audit_log.user_id:
                user = session.query(User).filter(User.id == audit_log.user_id).first()
            
            log_data = {
                'id': audit_log.id,
                'user_id': audit_log.user_id,
                'username': audit_log.username,
                'user_full_name': user.full_name if user else None,
                'user_email': user.email if user else None,
                'action': audit_log.action,
                'action_type': audit_log.action_type,
                'resource_type': audit_log.resource_type,
                'resource_id': audit_log.resource_id,
                'ip_address': audit_log.ip_address,
                'user_agent': audit_log.user_agent,
                'created_at': audit_log.created_at.isoformat() if audit_log.created_at else None,
                'old_value': audit_log.old_value,
                'new_value': audit_log.new_value,
                'changes': get_changes_summary(audit_log.old_value, audit_log.new_value)
            }
            
            return json({
                'success': True,
                'data': {
                    'audit_log': log_data
                },
                'message': 'Audit log retrieved successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit log detail: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@audit_logs_bp.route('/stats', methods=['GET'])
@require_auth
@require_role('admin')
async def get_audit_log_stats(req: request.Request):
    """
    Get audit log statistics
    
    Query Parameters:
    - date_from: Filter from date (default: last 7 days)
    - date_to: Filter to date (default: today)
    
    Returns:
    {
        "success": true,
        "data": {
            "total_logs": 1000,
            "by_action_type": {...},
            "by_resource_type": {...},
            "top_users": [...]
        }
    }
    """
    try:
        # Parse query parameters
        date_from = req.args.get('date_from', '')
        date_to = req.args.get('date_to', '')
        
        # Default to last 7 days if not specified
        if not date_from:
            date_from = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not date_to:
            date_to = datetime.utcnow().isoformat()
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build base query
            query = session.query(AuditLog)
            
            try:
                from_date = datetime.fromisoformat(date_from)
                to_date = datetime.fromisoformat(date_to)
                query = query.filter(
                    AuditLog.created_at >= from_date,
                    AuditLog.created_at <= to_date
                )
            except:
                pass
            
            # Get total count
            total_logs = query.count()
            
            # Count by action type
            action_type_stats = {}
            for action_type in ['create', 'update', 'delete', 'view', 'export']:
                count = query.filter(AuditLog.action_type == action_type).count()
                if count > 0:
                    action_type_stats[action_type] = count
            
            # Count by resource type
            resource_type_stats = {}
            for resource_type in ['customer', 'pricing', 'settlement', 'user', 'payment']:
                count = query.filter(AuditLog.resource_type == resource_type).count()
                if count > 0:
                    resource_type_stats[resource_type] = count
            
            # Get top users
            top_users = []
            user_counts = session.query(
                AuditLog.user_id,
                AuditLog.username
            ).filter(
                AuditLog.user_id.isnot(None)
            ).group_by(
                AuditLog.user_id,
                AuditLog.username
            ).order_by(
                session.query(AuditLog).filter(
                    AuditLog.user_id == AuditLog.user_id
                ).count().desc()
            ).limit(10).all()
            
            for user_id, username in user_counts:
                top_users.append({
                    'user_id': user_id,
                    'username': username,
                    'count': session.query(AuditLog).filter(
                        AuditLog.user_id == user_id
                    ).count()
                })
            
            return json({
                'success': True,
                'data': {
                    'total_logs': total_logs,
                    'by_action_type': action_type_stats,
                    'by_resource_type': resource_type_stats,
                    'top_users': top_users,
                    'date_range': {
                        'from': date_from,
                        'to': date_to
                    }
                },
                'message': 'Audit log statistics retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to get audit log statistics: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


def get_changes_summary(old_value: dict, new_value: dict) -> list:
    """
    Get summary of changes between old and new values
    
    Args:
        old_value: Old value dictionary
        new_value: New value dictionary
        
    Returns:
        List of changed fields with before/after values
    """
    if not old_value or not new_value:
        return []
    
    changes = []
    
    # Get all keys from both dictionaries
    all_keys = set(list(old_value.keys()) + list(new_value.keys()))
    
    for key in all_keys:
        old_val = old_value.get(key)
        new_val = new_value.get(key)
        
        if old_val != new_val:
            changes.append({
                'field': key,
                'old_value': old_val,
                'new_value': new_val
            })
    
    return changes


def log_audit(
    session,
    user_id: int,
    username: str,
    action: str,
    action_type: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Helper function to create audit log entry
    
    Args:
        session: Database session
        user_id: User ID
        username: Username
        action: Action description
        action_type: Type of action (create, update, delete, view, export)
        resource_type: Type of resource (customer, pricing, settlement, user)
        resource_id: Resource ID (optional)
        old_value: Old value before change (optional)
        new_value: New value after change (optional)
        ip_address: IP address (optional)
        user_agent: User agent string (optional)
    """
    try:
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        session.add(audit_log)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        session.rollback()
