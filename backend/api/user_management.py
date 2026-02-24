# OP_CMS User Management API
# Story 5.1: User Account Management

from sanic import Blueprint, json, request
from sanic.exceptions import NotFound, BadRequest, Unauthorized
from typing import Optional
import logging
import uuid

from backend.models.database_models import User
from backend.dao.database_dao import DatabaseSessionFactory
from backend.utils.jwt import require_auth, require_role

logger = logging.getLogger(__name__)

user_management_bp = Blueprint('user_management', url_prefix='/users')


@user_management_bp.route('', methods=['GET'])
@require_auth
@require_role('admin', 'supervisor')
async def list_users(req: request.Request):
    """
    List all users
    
    Query Parameters:
    - role: Filter by role
    - is_active: Filter by active status
    
    Returns:
    {
        "success": true,
        "data": {
            "users": [...],
            "total": 10
        }
    }
    """
    try:
        role_filter = req.args.get('role', '')
        is_active_filter = req.args.get('is_active', '')
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Build query
            query = session.query(User)
            
            if role_filter:
                query = query.filter(User.role == role_filter)
            
            if is_active_filter:
                is_active = is_active_filter.lower() == 'true'
                query = query.filter(User.is_active == is_active)
            
            users = query.all()
            
            # Convert to response format
            users_data = [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone': user.phone,
                    'role': user.role,
                    'is_active': user.is_active,
                    'is_superuser': user.is_superuser,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
                }
                for user in users
            ]
            
            return json({
                'success': True,
                'data': {
                    'users': users_data,
                    'total': len(users_data)
                },
                'message': 'Users retrieved successfully'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@user_management_bp.route('', methods=['POST'])
@require_auth
@require_role('admin')
async def create_user(req: request.Request):
    """
    Create new user
    
    Request Body:
    {
        "username": "string (required, unique)",
        "email": "string (required, unique)",
        "password": "string (required, min 8 chars)",
        "full_name": "string",
        "phone": "string",
        "role": "string (operator, supervisor, admin)"
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
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return json({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': f'{field} is required'
                }, status=400)
        
        # Validate password length
        if len(data['password']) < 8:
            return json({
                'success': False,
                'error': 'Invalid password',
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Check if username or email already exists
            existing_user = session.query(User).filter(
                (User.username == data['username']) | 
                (User.email == data['email'])
            ).first()
            
            if existing_user:
                return json({
                    'success': False,
                    'error': 'User already exists',
                    'message': 'Username or email already registered'
                }, status=409)
            
            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email'],
                full_name=data.get('full_name'),
                phone=data.get('phone'),
                role=data.get('role', 'operator')
            )
            
            # Hash and set password
            new_user.set_password(data['password'])
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            return json({
                'success': True,
                'data': {
                    'user': new_user.to_dict()
                },
                'message': 'User created successfully'
            }, status=201)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@user_management_bp.route('/<user_id:int>', methods=['PUT'])
@require_auth
@require_role('admin')
async def update_user(req: request.Request, user_id: int):
    """
    Update user information
    
    Request Body:
    {
        "full_name": "string",
        "phone": "string",
        "role": "string",
        "is_active": boolean
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
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Find user
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFound("User not found")
            
            # Update fields
            if 'full_name' in data:
                user.full_name = data['full_name']
            
            if 'phone' in data:
                user.phone = data['phone']
            
            if 'role' in data:
                user.role = data['role']
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            session.commit()
            session.refresh(user)
            
            return json({
                'success': True,
                'data': {
                    'user': user.to_dict()
                },
                'message': 'User updated successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@user_management_bp.route('/<user_id:int>', methods=['DELETE'])
@require_auth
@require_role('admin')
async def delete_user(req: request.Request, user_id: int):
    """
    Delete user account
    
    Returns:
    {
        "success": true,
        "message": "User deleted successfully"
    }
    """
    try:
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Find user
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFound("User not found")
            
            # Prevent deleting own account
            current_user_id = getattr(req, 'current_user', {}).get('user_id')
            if user.id == current_user_id:
                return json({
                    'success': False,
                    'error': 'Cannot delete own account',
                    'message': 'You cannot delete your own account'
                }, status=400)
            
            # Delete user
            session.delete(user)
            session.commit()
            
            return json({
                'success': True,
                'message': 'User deleted successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@user_management_bp.route('/<user_id:int>/reset-password', methods=['POST'])
@require_auth
@require_role('admin')
async def reset_password(req: request.Request, user_id: int):
    """
    Reset user password
    
    Request Body:
    {
        "new_password": "string (required, min 8 chars)"
    }
    
    Returns:
    {
        "success": true,
        "message": "Password reset successfully"
    }
    """
    try:
        data = req.json
        
        # Validate new password
        new_password = data.get('new_password')
        if not new_password:
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'new_password is required'
            }, status=400)
        
        if len(new_password) < 8:
            return json({
                'success': False,
                'error': 'Invalid password',
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Find user
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise NotFound("User not found")
            
            # Set new password
            user.set_password(new_password)
            session.commit()
            
            return json({
                'success': True,
                'message': 'Password reset successfully'
            })
            
        finally:
            session.close()
            
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Failed to reset password: {str(e)}")
        return json({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
