# OP_CMS User Permissions API
# Story 5.2: Role Assignment & Permission Control

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Forbidden
from typing import Optional, List, Dict
import logging
from functools import wraps

from backend.models.database_models import User
from backend.dao.database_dao import DatabaseSessionFactory
from backend.utils.jwt import verify_token

logger = logging.getLogger(__name__)

permissions_bp = Blueprint('permissions', url_prefix='/permissions')


# Role definitions with permissions
ROLES = {
    'admin': {
        'name': '系统管理员',
        'permissions': [
            'view_customer', 'edit_customer', 'delete_customer',
            'view_pricing', 'edit_pricing',
            'view_settlement', 'approve_settlement',
            'view_reports', 'export_reports',
            'manage_users', 'manage_roles'
        ]
    },
    'supervisor': {
        'name': '运营主管',
        'permissions': [
            'view_customer', 'edit_customer',
            'view_pricing', 'edit_pricing',
            'view_settlement', 'approve_settlement',
            'view_reports', 'export_reports'
        ]
    },
    'operator': {
        'name': '运营人员',
        'permissions': [
            'view_customer', 'edit_customer',
            'view_pricing',
            'view_settlement',
            'view_reports'
        ]
    },
    'viewer': {
        'name': '普通用户',
        'permissions': [
            'view_customer',
            'view_reports'
        ]
    }
}


def check_permission(required_permission: str):
    """
    Decorator to check if user has required permission
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(req, *args, **kwargs):
            # Get current user
            current_user = getattr(req, 'current_user', None)
            
            if not current_user:
                raise Forbidden("Authentication required")
            
            # Get user role
            role = current_user.get('role', 'viewer')
            
            # Check if role has permission
            role_permissions = ROLES.get(role, {}).get('permissions', [])
            
            if required_permission not in role_permissions and role != 'admin':
                raise Forbidden(f"Permission denied: {required_permission}")
            
            return await f(req, *args, **kwargs)
        
        return decorated_function
    return decorator


@permissions_bp.route('/roles', methods=['GET'])
async def get_roles(req: request.Request):
    """
    Get all available roles
    
    Returns:
    {
        "success": true,
        "data": {
            "roles": [
                {
                    "id": "admin",
                    "name": "系统管理员",
                    "permissions": [...]
                }
            ]
        }
    }
    """
    try:
        roles_data = [
            {
                'id': role_id,
                'name': role_info['name'],
                'permissions': role_info['permissions']
            }
            for role_id, role_info in ROLES.items()
        ]
        
        return json({
            'success': True,
            'data': {
                'roles': roles_data
            },
            'message': 'Roles retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get roles: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@permissions_bp.route('/permissions', methods=['GET'])
async def get_permissions(req: request.Request):
    """
    Get all available permissions
    
    Returns:
    {
        "success": true,
        "data": {
            "permissions": [
                {
                    "id": "view_customer",
                    "name": "查看客户",
                    "category": "customer"
                }
            ]
        }
    }
    """
    try:
        # Define permission categories
        permission_categories = {
            'customer': '客户管理',
            'pricing': '定价配置',
            'settlement': '结算管理',
            'reports': '报表管理',
            'admin': '系统管理'
        }
        
        # Get unique permissions with categories
        all_permissions = {}
        for role_info in ROLES.values():
            for perm in role_info['permissions']:
                if perm not in all_permissions:
                    # Determine category
                    category = 'other'
                    for cat, cat_name in permission_categories.items():
                        if perm.startswith(cat) or perm.startswith('manage'):
                            category = cat
                            break
                    
                    all_permissions[perm] = {
                        'id': perm,
                        'name': perm.replace('_', ' ').title(),
                        'category': category,
                        'category_name': permission_categories.get(category, '其他')
                    }
        
        return json({
            'success': True,
            'data': {
                'permissions': list(all_permissions.values()),
                'categories': [
                    {'id': k, 'name': v} 
                    for k, v in permission_categories.items()
                ]
            },
            'message': 'Permissions retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to get permissions: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@permissions_bp.route('/users/<user_id:int>/role', methods=['PUT'])
async def update_user_role(req: request.Request, user_id: int):
    """
    Update user role
    
    Request Body:
    {
        "role": "operator"  // admin, supervisor, operator, viewer
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "user": {...}
        }
    }
    """
    try:
        data = req.json
        new_role = data.get('role')
        
        if not new_role or new_role not in ROLES:
            return json({
                'success': False,
                'error': 'Invalid role',
                'message': f'Invalid role: {new_role}. Valid roles: {list(ROLES.keys())}'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Find user
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFound("User not found")
            
            # Update role
            user.role = new_role
            session.commit()
            session.refresh(user)
            
            return json({
                'success': True,
                'data': {
                    'user': user.to_dict()
                },
                'message': 'User role updated successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@permissions_bp.route('/check', methods=['POST'])
async def check_user_permission(req: request.Request):
    """
    Check if current user has specific permission
    
    Request Body:
    {
        "permission": "edit_customer",
        "resource_type": "customer",  // optional
        "resource_id": 1  // optional
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "has_permission": true,
            "permission": "edit_customer",
            "role": "operator"
        }
    }
    """
    try:
        data = req.json
        permission = data.get('permission')
        
        if not permission:
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'permission is required'
            }, status=400)
        
        # Get current user from token
        auth_header = req.headers.get('Authorization')
        if not auth_header:
            return json({
                'success': False,
                'data': {
                    'has_permission': False,
                    'reason': 'No authentication'
                }
            })
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() == 'bearer':
                payload = verify_token(token)
                if payload:
                    role = payload.get('role', 'viewer')
                    role_permissions = ROLES.get(role, {}).get('permissions', [])
                    has_permission = permission in role_permissions or role == 'admin'
                    
                    return json({
                        'success': True,
                        'data': {
                            'has_permission': has_permission,
                            'permission': permission,
                            'role': role,
                            'user_id': payload.get('user_id')
                        }
                    })
        except:
            pass
        
        return json({
            'success': True,
            'data': {
                'has_permission': False,
                'reason': 'Invalid or expired token'
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to check permission: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
