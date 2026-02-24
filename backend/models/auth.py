# OP_CMS Authentication Models
# Story: User Authentication & Authorization

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt
import secrets

from backend.models.database_models import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="Username")
    email = Column(String(100), unique=True, nullable=False, comment="Email address")
    password_hash = Column(String(255), nullable=False, comment="Bcrypt password hash")
    
    # User information
    full_name = Column(String(100), comment="Full name")
    phone = Column(String(20), comment="Phone number")
    
    # Account status
    is_active = Column(Boolean, default=True, comment="Is account active")
    is_superuser = Column(Boolean, default=False, comment="Is superuser (admin)")
    
    # Role (for RBAC)
    role = Column(String(50), default='operator', comment="Role: admin, supervisor, operator, viewer")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, comment="Creation timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Update timestamp")
    last_login_at = Column(DateTime, comment="Last login timestamp")
    
    # Relationships
    access_logs = relationship("AccessLog", back_populates="user")
    customer_access = relationship("CustomerAccess", back_populates="user")
    
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary (exclude password)"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }
        
        if include_sensitive:
            data['is_superuser'] = self.is_superuser
        
        return data
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class AccessLog(Base):
    """Access log for audit trail"""
    __tablename__ = 'access_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment="User ID")
    
    # Action details
    action = Column(String(50), nullable=False, comment="Action: login, logout, view, edit, delete, export")
    resource_type = Column(String(50), comment="Resource type: customer, pricing, etc.")
    resource_id = Column(Integer, comment="Resource ID")
    accessed_fields = Column(String(500), comment="Accessed fields (JSON)")
    
    # Request info
    ip_address = Column(String(45), comment="IP address")
    user_agent = Column(String(500), comment="User agent string")
    
    # Result
    status_code = Column(Integer, comment="HTTP status code")
    error_message = Column(String(500), comment="Error message if failed")
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="Access timestamp")
    
    # Relationships
    user = relationship("User", back_populates="access_logs")
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'status_code': self.status_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CustomerAccess(Base):
    """Customer-level access control"""
    __tablename__ = 'customer_access'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, comment="Customer ID")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment="User ID")
    
    # Access level
    access_level = Column(String(20), nullable=False, default='masked', 
                         comment="Access level: full, masked, none")
    
    # Grant info
    granted_by = Column(Integer, ForeignKey('users.id'), comment="Granted by user ID")
    granted_at = Column(DateTime, default=datetime.utcnow, comment="Granted timestamp")
    
    # Unique constraint
    __table_args__ = (
        # Prevent duplicate customer-user pairs
        # UniqueConstraint('customer_id', 'user_id', name='unique_customer_user'),
    )
    
    # Relationships
    user = relationship("User", back_populates="customer_access", foreign_keys=[user_id])
    customer = relationship("Customer", backref="access_grants")
    granter = relationship("User", foreign_keys=[granted_by])
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'access_level': self.access_level,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
        }
