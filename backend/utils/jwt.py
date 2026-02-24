# OP_CMS JWT Utilities
# JSON Web Token handling for authentication

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = "your-super-secret-key-change-this-in-production"  # TODO: Load from environment
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Token payload data (should include user_id, username, role)
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Token payload data
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Check expiration (automatically done by PyJWT, but double-check)
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token has expired")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify access token and return payload
    
    Args:
        token: JWT access token
        
    Returns:
        User payload if valid, None otherwise
    """
    return decode_token(token, token_type="access")


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Use refresh token to create new access token
    
    Args:
        refresh_token: JWT refresh token
        
    Returns:
        New access token if refresh token is valid, None otherwise
    """
    payload = decode_token(refresh_token, token_type="refresh")
    
    if not payload:
        return None
    
    # Create new access token with same user data
    user_data = {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "role": payload.get("role")
    }
    
    return create_access_token(user_data)


# Decorator for protecting routes
def require_auth(f):
    """
    Decorator to require authentication for a route
    
    Usage:
        @customer_bp.route('/protected', methods=['GET'])
        @require_auth
        async def protected_route(request):
            # request.current_user is available
            pass
    """
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            from sanic.exceptions import Unauthorized
            raise Unauthorized("Missing Authorization header")
        
        # Extract token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                from sanic.exceptions import Unauthorized
                raise Unauthorized("Invalid authentication scheme")
        except ValueError:
            from sanic.exceptions import Unauthorized
            raise Unauthorized("Invalid Authorization header format")
        
        # Verify token
        payload = verify_token(token)
        
        if not payload:
            from sanic.exceptions import Unauthorized
            raise Unauthorized("Invalid or expired token")
        
        # Attach user info to request
        request.current_user = {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'role': payload.get('role')
        }
        
        # Call original function
        return await f(request, *args, **kwargs)
    
    return decorated_function


def require_role(*allowed_roles: str):
    """
    Decorator to require specific roles for a route
    
    Usage:
        @customer_bp.route('/admin-only', methods=['GET'])
        @require_role('admin', 'supervisor')
        async def admin_route(request):
            # Only admin and supervisor can access
            pass
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, 'current_user') or not request.current_user:
                from sanic.exceptions import Unauthorized
                raise Unauthorized("Authentication required")
            
            # Check role
            user_role = request.current_user.get('role')
            if user_role not in allowed_roles:
                from sanic.exceptions import Forbidden
                raise Forbidden(f"Role {user_role} not authorized. Required: {', '.join(allowed_roles)}")
            
            return await f(request, *args, **kwargs)
        
        return decorated_function
    return decorator
