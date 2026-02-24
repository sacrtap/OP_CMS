# OP_CMS Permission Utilities
# Story 1.5: Customer Access Control

import re
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class UserRole(Enum):
    """User role definitions"""
    ADMIN = 'admin'  # Full access
    SUPERVISOR = 'supervisor'  # Can assign permissions
    OPERATOR = 'operator'  # Standard operations
    VIEWER = 'viewer'  # Read-only with masking


class AccessLevel(Enum):
    """Data access levels"""
    FULL = 'full'  # All fields visible
    MASKED = 'masked'  # Sensitive fields masked
    NONE = 'none'  # No access


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy
    Format: 138****8000
    
    Args:
        phone: Raw phone number
        
    Returns:
        Masked phone number
    """
    if not phone:
        return phone
    
    # Remove non-digit characters
    cleaned = re.sub(r'[\+\-\(\)\s]', '', phone)
    
    # If Chinese mobile (11 digits starting with 1)
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return f'{cleaned[:3]}****{cleaned[-4:]}'
    
    # Other formats - mask middle
    if len(cleaned) > 7:
        return f'{cleaned[:3]}****{cleaned[-4:]}'
    
    return '****'


def mask_email(email: str) -> str:
    """
    Mask email address for privacy
    Format: tes****@example.com
    
    Args:
        email: Raw email address
        
    Returns:
        Masked email address
    """
    if not email or '@' not in email:
        return email
    
    try:
        name, domain = email.rsplit('@', 1)
        
        if len(name) > 2:
            masked_name = f'{name[0]}****{name[-1]}'
        elif len(name) == 2:
            masked_name = f'{name[0]}****'
        else:
            masked_name = '****'
        
        return f'{masked_name}@{domain}'
    
    except:
        return '****'


def mask_credit_code(code: str) -> str:
    """
    Mask unified social credit code
    Format: 9131****MA1K3YJ12X
    
    Args:
        code: Raw credit code (18 characters)
        
    Returns:
        Masked credit code
    """
    if not code or len(code) != 18:
        return code
    
    # Show first 4 and last 10 characters
    return f'{code[:4]}****{code[4:]}'


def mask_sensitive_data(data: Dict[str, Any], access_level: AccessLevel) -> Dict[str, Any]:
    """
    Mask sensitive fields in customer data based on access level
    
    Args:
        data: Customer data dictionary
        access_level: User's access level
        
    Returns:
        Customer data with appropriate masking
    """
    if access_level == AccessLevel.FULL:
        return data.copy()
    
    if access_level == AccessLevel.NONE:
        return {'error': 'No access permission'}
    
    # MASKED access level
    masked = data.copy()
    
    if 'contact_phone' in masked:
        masked['contact_phone'] = mask_phone(masked['contact_phone'])
    
    if 'email' in masked:
        masked['email'] = mask_email(masked['email'])
    
    if 'credit_code' in masked:
        masked['credit_code'] = mask_credit_code(masked['credit_code'])
    
    return masked


def check_role_permission(role: UserRole, required_permission: str) -> bool:
    """
    Check if user role has required permission
    
    Args:
        role: User role
        required_permission: Permission string (view, edit, delete, assign)
        
    Returns:
        True if role has permission
    """
    permissions = {
        UserRole.ADMIN: {'view', 'edit', 'delete', 'assign', 'manage'},
        UserRole.SUPERVISOR: {'view', 'edit', 'assign'},
        UserRole.OPERATOR: {'view', 'edit'},
        UserRole.VIEWER: {'view'}
    }
    
    return required_permission in permissions.get(role, set())


class PermissionDenied(Exception):
    """Exception raised when permission check fails"""
    def __init__(self, message: str, required_permission: str = None):
        super().__init__(message)
        self.required_permission = required_permission
