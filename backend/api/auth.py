# OP_CMS Authentication API
# User authentication endpoints

from sanic import Blueprint, json, request
from sanic.exceptions import Unauthorized, Forbidden, BadRequest
from datetime import datetime
import logging

from backend.models.database_models import Database_session_factory
from backend.models.auth import User, AccessLog
from backend.utils.jwt import create_access_token, create_refresh_token, verify_token, refresh_access_token
from backend.utils.permissions import check_role_permission

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', url_prefix='/api/v1/auth')


@auth_bp.route('/register', methods=['POST'])
async def register(req: request.Request):
    """
    Register new user
    
    Request Body:
    {
        "username": "string (required, unique)",
        "email": "string (required, unique)",
        "password": "string (required, min 8 chars)",
        "full_name": "string (optional)",
        "phone": "string (optional)",
        "role": "string (optional, default: operator)"
    }
    """
    try:
        data = req.json
        
        # Validate required fields
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return json({
                'success': False,
                'error': 'Missing required fields',
                'message': 'username, email, and password are required'
            }, status=400)
        
        # Validate password length
        if len(data['password']) < 8:
            return json({
                'success': False,
                'error': 'Invalid password',
                'message': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Get database session
        session_factory = Database_session_factory()
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
            
            # Log registration
            log_access(session, new_user.id, 'register', success=True)
            
            # Create tokens
            user_data = {
                'user_id': new_user.id,
                'username': new_user.username,
                'role': new_user.role
            }
            
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
            
            return json({
                'success': True,
                'data': {
                    'user': new_user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                },
                'message': 'User registered successfully'
            }, status=201)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return json({
            'success': False,
            'error': 'Registration failed',
            'message': str(e)
        }, status=500)


@auth_bp.route('/login', methods=['POST'])
async def login(req: request.Request):
    """
    Login user
    
    Request Body:
    {
        "username": "string (required)",
        "password": "string (required)"
    }
    """
    try:
        data = req.json
        
        if not data.get('username') or not data.get('password'):
            return json({
                'success': False,
                'error': 'Missing credentials',
                'message': 'Username and password are required'
            }, status=400)
        
        # Get database session
        session_factory = Database_session_factory()
        session = session_factory.get_session()
        
        try:
            # Find user
            user = session.query(User).filter(User.username == data['username']).first()
            
            if not user:
                log_access(session, None, 'login', success=False, error_message='User not found', ip_address=req.ip)
                return json({
                    'success': False,
                    'error': 'Invalid credentials',
                    'message': 'Invalid username or password'
                }, status=401)
            
            # Verify password
            if not user.verify_password(data['password']):
                log_access(session, user.id, 'login', success=False, error_message='Invalid password', ip_address=req.ip)
                return json({
                    'success': False,
                    'error': 'Invalid credentials',
                    'message': 'Invalid username or password'
                }, status=401)
            
            # Check if user is active
            if not user.is_active:
                log_access(session, user.id, 'login', success=False, error_message='Account inactive', ip_address=req.ip)
                return json({
                    'success': False,
                    'error': 'Account inactive',
                    'message': 'Your account has been deactivated'
                }, status=403)
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            session.commit()
            
            # Log successful login
            log_access(session, user.id, 'login', success=True, ip_address=req.ip)
            
            # Create tokens
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role
            }
            
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
            
            return json({
                'success': True,
                'data': {
                    'user': user.to_dict(include_sensitive=True),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                },
                'message': 'Login successful'
            })
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return json({
            'success': False,
            'error': 'Login failed',
            'message': str(e)
        }, status=500)


@auth_bp.route('/refresh', methods=['POST'])
async def refresh_token_endpoint(req: request.Request):
    """
    Refresh access token using refresh token
    
    Request Body:
    {
        "refresh_token": "string (required)"
    }
    """
    try:
        data = req.json
        refresh_token_str = data.get('refresh_token')
        
        if not refresh_token_str:
            return json({
                'success': False,
                'error': 'Missing refresh token',
                'message': 'Refresh token is required'
            }, status=400)
        
        # Get new access token
        new_access_token = refresh_access_token(refresh_token_str)
        
        if not new_access_token:
            return json({
                'success': False,
                'error': 'Invalid refresh token',
                'message': 'Refresh token is invalid or expired'
            }, status=401)
        
        return json({
            'success': True,
            'data': {
                'access_token': new_access_token,
                'token_type': 'Bearer'
            }
        })
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return json({
            'success': False,
            'error': 'Token refresh failed',
            'message': str(e)
        }, status=500)


@auth_bp.route('/me', methods=['GET'])
async def get_current_user(req: request.Request):
    """
    Get current authenticated user info
    
    Requires: Bearer token in Authorization header
    """
    try:
        # Get token from header
        auth_header = req.headers.get('Authorization')
        
        if not auth_header:
            raise Unauthorized("Missing Authorization header")
        
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise Unauthorized("Invalid authentication scheme")
        
        # Verify token
        payload = verify_token(token)
        
        if not payload:
            raise Unauthorized("Invalid or expired token")
        
        # Get user from database
        session_factory = Database_session_factory()
        session = session_factory.get_session()
        
        try:
            user = session.query(User).filter(User.id == payload['user_id']).first()
            
            if not user or not user.is_active:
                raise Unauthorized("User not found or inactive")
            
            return json({
                'success': True,
                'data': user.to_dict(include_sensitive=True)
            })
            
        finally:
            session.close()
            
    except (Unauthorized, Forbidden) as e:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return json({
            'success': False,
            'error': 'Failed to get user info',
            'message': str(e)
        }, status=500)


@auth_bp.route('/logout', methods=['POST'])
async def logout(req: request.Request):
    """
    Logout user (client should delete token)
    
    Note: JWT is stateless, so logout is handled client-side by deleting tokens
    """
    try:
        # Get token from header
        auth_header = req.headers.get('Authorization')
        
        if auth_header:
            scheme, token = auth_header.split()
            if scheme.lower() == 'bearer':
                payload = verify_token(token)
                if payload:
                    # Log logout
                    session_factory = Database_session_factory()
                    session = session_factory.get_session()
                    try:
                        log_access(session, payload['user_id'], 'logout', success=True, ip_address=req.ip)
                    finally:
                        session.close()
        
        return json({
            'success': True,
            'message': 'Logout successful'
        })
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return json({
            'success': False,
            'error': 'Logout failed',
            'message': str(e)
        }, status=500)


def log_access(session, user_id: int, action: str, success: bool = True, 
               resource_type: str = None, resource_id: int = None,
               error_message: str = None, ip_address: str = None):
    """Helper function to log access"""
    try:
        log = AccessLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status_code=200 if success else 401,
            error_message=error_message,
            ip_address=ip_address
        )
        session.add(log)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to log access: {str(e)}")
