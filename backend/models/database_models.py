# OP_CMS Database Models
# MySQL 8.0+ ORM Model Definitions
# Python SQLAlchemy/Pydantic Format

"""
OP_CMS Database Models - MySQL 8.0+

This module contains the core data model definitions for the OP_CMS system.
The models are designed for MySQL 8.0+ and use SQLAlchemy ORM with Pydantic validation.

Database Schema: op_cms
Character Set: utf8mb4
Collation: utf8mb4_unicode_ci
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, DECIMAL, Boolean, ForeignKey,
    Text, JSON, Index, create_engine, text
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid

Base = declarative_base()


# ==================== Customer Models ====================

class Customer(Base):
    """Customer Information Model - Extended for Story 1.1"""
    __tablename__ = 'customers'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(36), unique=True, nullable=False, comment="Unique customer identifier (UUID)")
    
    # Core fields (required)
    company_name = Column(String(200), nullable=False, comment="Company name (required, unique)")
    contact_name = Column(String(100), nullable=False, comment="Contact person name (required)")
    contact_phone = Column(String(20), nullable=False, comment="Contact phone (required)")
    
    # Optional fields - Business identification
    credit_code = Column(String(50), unique=True, comment="Unified social credit code (18 digits, GB 32100-2015)")
    customer_type = Column(String(20), default='enterprise', comment="Customer type: enterprise, individual")
    
    # Optional fields - Location
    province = Column(String(50), comment="Province")
    city = Column(String(50), comment="City")
    address = Column(String(500), comment="Full address")
    
    # Optional fields - Contact information
    email = Column(String(100), comment="Email address")
    website = Column(String(200), comment="Company website")
    
    # Optional fields - Business information
    industry = Column(String(100), comment="Industry category")
    
    # Optional fields - ERP integration
    erp_system = Column(String(100), comment="ERP system name")
    erp_customer_code = Column(String(50), comment="Customer code in ERP system")
    
    # Optional fields - Customer attributes
    status = Column(String(20), default='active', comment="Status: active, inactive, potential")
    level = Column(String(20), default='standard', comment="Level: vip, standard, economy")
    source = Column(String(20), default='direct', comment="Source: direct, referral, marketing")
    remarks = Column(Text, comment="Additional remarks")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, comment="Creation timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Update timestamp")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_company_name', 'company_name'),
        Index('idx_customer_credit_code', 'credit_code'),
        Index('idx_customer_contact_name', 'contact_name'),
        Index('idx_customer_status', 'status'),
        Index('idx_customer_level', 'level'),
        Index('idx_customer_province', 'province'),
    )
    
    # Relationships
    price_configs = relationship("PriceConfig", back_populates="customer")
    settlement_records = relationship("SettlementRecord", back_populates="customer")


class CustomerCreate(BaseModel):
    """Create customer request model - Story 1.1"""
    # Required fields
    company_name: str = Field(..., min_length=1, max_length=200)
    contact_name: str = Field(..., min_length=1, max_length=100)
    contact_phone: str = Field(..., min_length=1, max_length=20)
    
    # Optional fields - Business identification
    credit_code: Optional[str] = Field(None, max_length=50)
    customer_type: Optional[str] = Field('enterprise', pattern="^(enterprise|individual)$")
    
    # Optional fields - Location
    province: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    
    # Optional fields - Contact information
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    
    # Optional fields - Business information
    industry: Optional[str] = Field(None, max_length=100)
    
    # Optional fields - ERP integration
    erp_system: Optional[str] = Field(None, max_length=100)
    erp_customer_code: Optional[str] = Field(None, max_length=50)
    
    # Optional fields - Customer attributes
    status: Optional[str] = Field('active', pattern="^(active|inactive|potential)$")
    level: Optional[str] = Field('standard', pattern="^(vip|standard|economy)$")
    source: Optional[str] = Field('direct', pattern="^(direct|referral|marketing)$")
    remarks: Optional[str] = None
    
    @field_validator('contact_phone')
    def validate_phone(cls, v):
        """Validate phone number format (Mainland China: +86 prefix, 11 digits)"""
        if v:
            cleaned = v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not cleaned.isdigit():
                raise ValueError('Phone number must contain only digits, spaces, +, -, and parentheses')
            if len(cleaned) < 8 or len(cleaned) > 15:
                raise ValueError('Phone number length must be between 8 and 15 digits')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        if v:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @field_validator('credit_code')
    def validate_credit_code(cls, v):
        """Validate unified social credit code (GB 32100-2015: 18 characters)"""
        if v:
            if len(v) != 18:
                raise ValueError('Unified social credit code must be 18 characters')
            # Basic format check: 18 alphanumeric characters
            if not v.isalnum():
                raise ValueError('Unified social credit code must contain only alphanumeric characters')
        return v


class CustomerUpdate(BaseModel):
    """Update customer request model - Story 1.1"""
    # All fields are optional for update
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    credit_code: Optional[str] = Field(None, max_length=50)
    customer_type: Optional[str] = Field(None, pattern="^(enterprise|individual)$")
    province: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    erp_system: Optional[str] = Field(None, max_length=100)
    erp_customer_code: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive|potential)$")
    level: Optional[str] = Field(None, pattern="^(vip|standard|economy)$")
    source: Optional[str] = Field(None, pattern="^(direct|referral|marketing)$")
    remarks: Optional[str] = None
    
    # Reuse validators from CustomerCreate
    _validate_phone = field_validator('contact_phone')(CustomerCreate.validate_phone)
    _validate_email = field_validator('email')(CustomerCreate.validate_email)
    _validate_credit_code = field_validator('credit_code')(CustomerCreate.validate_credit_code)


class CustomerResponse(BaseModel):
    """Customer response model - Story 1.1"""
    id: int
    customer_id: str
    company_name: str
    contact_name: str
    contact_phone: str
    credit_code: Optional[str] = None
    customer_type: str = 'enterprise'
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    erp_system: Optional[str] = None
    erp_customer_code: Optional[str] = None
    status: str = 'active'
    level: str = 'standard'
    source: str = 'direct'
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Customer list response with pagination - Story 1.1"""
    customers: List[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Price Config Models ====================

class PriceConfig(Base):
    """Price Configuration Model"""
    __tablename__ = 'price_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(36), unique=True, nullable=False, comment="Unique config identifier (UUID)")
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, comment="Customer reference")
    name = Column(String(100), nullable=False, comment="Configuration name")
    description = Column(Text, comment="Configuration description")
    price_model = Column(String(20), nullable=False, comment="Price model: tiered, volume, dynamic")
    currency = Column(String(3), default='CNY', comment="Currency code: CNY, USD, EUR")
    
    # Tiered pricing attributes
    min_quantity = Column(DECIMAL(10, 2), comment="Minimum quantity for this tier")
    max_quantity = Column(DECIMAL(10, 2), comment="Maximum quantity for this tier")
    unit_price = Column(DECIMAL(12, 4), comment="Unit price for this tier")
    
    # Volume pricing attributes
    base_price = Column(DECIMAL(12, 4), comment="Base price for volume pricing")
    volume_discount = Column(DECIMAL(5, 2), comment="Volume discount percentage")
    
    # Dynamic pricing attributes
    pricing_rules = Column(JSON, comment="Dynamic pricing rules in JSON format")
    
    is_active = Column(Boolean, default=True, comment="Is this configuration active?")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_price_config_customer', 'customer_id'),
        Index('idx_price_config_active', 'is_active'),
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="price_configs")
    settlement_records = relationship("SettlementRecord", back_populates="price_config")


class PriceConfigCreate(BaseModel):
    """Create price config request model"""
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: int = Field(...)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    price_model: str = Field(..., pattern="^(tiered|volume|dynamic)$")
    currency: Optional[str] = Field('CNY', pattern="^(CNY|USD|EUR)$")
    
    # Price model specific fields
    min_quantity: Optional[Decimal] = Field(None)
    max_quantity: Optional[Decimal] = Field(None)
    unit_price: Optional[Decimal] = Field(None)
    base_price: Optional[Decimal] = Field(None)
    volume_discount: Optional[Decimal] = Field(None)
    pricing_rules: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_active: Optional[bool] = Field(True)


# ==================== Settlement Record Models ====================

class SettlementRecord(Base):
    """Settlement Record Model"""
    __tablename__ = 'settlement_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(36), unique=True, nullable=False, comment="Unique record identifier (UUID)")
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    config_id = Column(Integer, ForeignKey('price_configs.id'), nullable=False)
    
    # Usage data
    period_start = Column(DateTime, nullable=False, comment="Settlement period start")
    period_end = Column(DateTime, nullable=False, comment="Settlement period end")
    usage_quantity = Column(DECIMAL(10, 2), nullable=False, comment="Total usage quantity")
    unit = Column(String(20), nullable=False, comment="Usage unit: GB, hours, calls, etc.")
    
    # Pricing information
    price_model = Column(String(20), nullable=False, comment="Price model at settlement time")
    unit_price = Column(DECIMAL(12, 4), nullable=False, comment="Unit price used for calculation")
    total_amount = Column(DECIMAL(12, 2), nullable=False, comment="Total settlement amount")
    currency = Column(String(3), default='CNY', comment="Currency code")
    
    # Settlement status
    status = Column(String(20), default='pending', comment="Status: pending, approved, paid, cancelled")
    remarks = Column(Text, comment="Settlement remarks")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, comment="Approval timestamp")
    paid_at = Column(DateTime, comment="Payment timestamp")
    
    # Indexes
    __table_args__ = (
        Index('idx_settlement_customer', 'customer_id'),
        Index('idx_settlement_period', 'period_start', 'period_end'),
        Index('idx_settlement_status', 'status'),
        Index('idx_settlement_record_id', 'record_id'),
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="settlement_records")
    price_config = relationship("PriceConfig", back_populates="settlement_records")


class SettlementRecordCreate(BaseModel):
    """Create settlement record request model"""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: int = Field(...)
    config_id: int = Field(...)
    period_start: datetime = Field(...)
    period_end: datetime = Field(...)
    usage_quantity: Decimal = Field(...)
    unit: str = Field(..., min_length=1, max_length=20)
    price_model: str = Field(..., pattern="^(tiered|volume|dynamic)$")
    unit_price: Decimal = Field(...)
    total_amount: Decimal = Field(...)
    currency: Optional[str] = Field('CNY')
    status: Optional[str] = Field('pending', pattern="^(pending|approved|paid|cancelled)$")
    remarks: Optional[str] = Field(None)


# ==================== Database Connection ====================

class DatabaseConnection:
    """Database connection and session management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection"""
        # Build connection string
        db_host = self.config.get('DB_HOST', 'localhost')
        db_port = self.config.get('DB_PORT', 3306)
        db_name = self.config.get('DB_NAME', 'op_cms')
        db_user = self.config.get('DB_USER', 'root')
        db_password = self.config.get('DB_PASSWORD', 'password')
        charset = self.config.get('CHARSET', 'utf8mb4')
        collation = self.config.get('COLLATION', 'utf8mb4_unicode_ci')
        
        self.connection_string = (
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            f"?charset={charset}&collation={collation}"
        )
        
        # Create engine
        self.engine = create_engine(
            self.connection_string,
            pool_size=self.config.get('POOL_SIZE', 5),
            pool_timeout=self.config.get('POOL_TIMEOUT', 30),
            pool_pre_ping=True,
            echo=False
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def init_database(self):
        """Initialize database schema"""
        Base.metadata.create_all(bind=self.engine)
        print("Database schema initialized successfully")
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            print("Database connection closed")


# ==================== Migration Scripts (Example) ====================

"""
MySQL Migration Script Example
-------------------------------

-- Create database
CREATE DATABASE IF NOT EXISTS `op_cms` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use database
USE `op_cms`;

-- Create customers table
CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `customer_id` VARCHAR(36) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `contact_type` VARCHAR(20) NOT NULL,
    `contact_name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20),
    `email` VARCHAR(100),
    `address` VARCHAR(500),
    `status` VARCHAR(20) DEFAULT 'active',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `metadata` JSON,
    INDEX `idx_customer_name` (`name`),
    INDEX `idx_customer_contact` (`contact_name`),
    INDEX `idx_customer_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create price_configs table
CREATE TABLE IF NOT EXISTS `price_configs` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `config_id` VARCHAR(36) NOT NULL UNIQUE,
    `customer_id` INT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT,
    `price_model` VARCHAR(20) NOT NULL,
    `currency` VARCHAR(3) DEFAULT 'CNY',
    `min_quantity` DECIMAL(10, 2),
    `max_quantity` DECIMAL(10, 2),
    `unit_price` DECIMAL(12, 4),
    `base_price` DECIMAL(12, 4),
    `volume_discount` DECIMAL(5, 2),
    `pricing_rules` JSON,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_price_config_customer` (`customer_id`),
    INDEX `idx_price_config_active` (`is_active`),
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create settlement_records table
CREATE TABLE IF NOT EXISTS `settlement_records` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `record_id` VARCHAR(36) NOT NULL UNIQUE,
    `customer_id` INT NOT NULL,
    `config_id` INT NOT NULL,
    `period_start` DATETIME NOT NULL,
    `period_end` DATETIME NOT NULL,
    `usage_quantity` DECIMAL(10, 2) NOT NULL,
    `unit` VARCHAR(20) NOT NULL,
    `price_model` VARCHAR(20) NOT NULL,
    `unit_price` DECIMAL(12, 4) NOT NULL,
    `total_amount` DECIMAL(12, 2) NOT NULL,
    `currency` VARCHAR(3) DEFAULT 'CNY',
    `status` VARCHAR(20) DEFAULT 'pending',
    `remarks` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `approved_at` DATETIME,
    `paid_at` DATETIME,
    INDEX `idx_settlement_customer` (`customer_id`),
    INDEX `idx_settlement_period` (`period_start`, `period_end`),
    INDEX `idx_settlement_status` (`status`),
    INDEX `idx_settlement_record_id` (`record_id`),
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`config_id`) REFERENCES `price_configs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data (example)
INSERT INTO `customers` (`customer_id`, `name`, `contact_type`, `contact_name`, `phone`, `email`, `status`)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', 'Test Customer 1', 'individual', 'John Doe', '+86-13800138000', 'john@example.com', 'active'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Test Customer 2', 'corporate', 'Jane Smith', '+86-13900139000', 'jane@example.com', 'active');

"""
