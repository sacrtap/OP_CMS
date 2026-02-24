"""Initial database schema - Story 0-2 + Auth models

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table('customers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_id', sa.String(36), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=False),
        sa.Column('contact_name', sa.String(100), nullable=False),
        sa.Column('contact_phone', sa.String(20), nullable=False),
        sa.Column('credit_code', sa.String(50), nullable=True),
        sa.Column('customer_type', sa.String(20), server_default='enterprise', nullable=False),
        sa.Column('province', sa.String(50), nullable=True),
        sa.Column('city', sa.String(50), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('website', sa.String(200), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('erp_system', sa.String(100), nullable=True),
        sa.Column('erp_customer_code', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('level', sa.String(20), server_default='standard', nullable=False),
        sa.Column('source', sa.String(20), server_default='direct', nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_id'),
        sa.UniqueConstraint('credit_code')
    )
    
    # Create indexes for customers
    op.create_index('idx_customer_company_name', 'customers', ['company_name'])
    op.create_index('idx_customer_credit_code', 'customers', ['credit_code'])
    op.create_index('idx_customer_contact_name', 'customers', ['contact_name'])
    op.create_index('idx_customer_status', 'customers', ['status'])
    op.create_index('idx_customer_level', 'customers', ['level'])
    op.create_index('idx_customer_province', 'customers', ['province'])
    
    # Create price_configs table
    op.create_table('price_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('config_id', sa.String(36), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_model', sa.String(20), server_default='single', nullable=False),
        sa.Column('device_series', sa.String(10), server_default='X', nullable=False),
        sa.Column('currency', sa.String(3), server_default='CNY', nullable=False),
        sa.Column('min_quantity', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('max_quantity', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('unit_price', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('base_price', sa.DECIMAL(12, 4), nullable=True),
        sa.Column('volume_discount', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('pricing_rules', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_id'),
        sa.UniqueConstraint('customer_id', 'device_series', name='unique_customer_device'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE')
    )
    
    # Create indexes for price_configs
    op.create_index('idx_price_config_customer', 'price_configs', ['customer_id'])
    op.create_index('idx_price_config_active', 'price_configs', ['is_active'])
    op.create_index('idx_price_config_model', 'price_configs', ['price_model'])
    op.create_index('idx_price_config_series', 'price_configs', ['device_series'])
    
    # Create settlement_records table
    op.create_table('settlement_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.String(36), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('usage_quantity', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('price_model', sa.String(20), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('total_amount', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='CNY', nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('record_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['config_id'], ['price_configs.id'], ondelete='CASCADE')
    )
    
    # Create indexes for settlement_records
    op.create_index('idx_settlement_customer', 'settlement_records', ['customer_id'])
    op.create_index('idx_settlement_period', 'settlement_records', ['period_start', 'period_end'])
    op.create_index('idx_settlement_status', 'settlement_records', ['status'])
    op.create_index('idx_settlement_record_id', 'settlement_records', ['record_id'])
    op.create_index('idx_settlement_customer_period', 'settlement_records', ['customer_id', 'period_start', 'period_end'])
    op.create_index('idx_settlement_customer_status', 'settlement_records', ['customer_id', 'status'])
    
    # Create users table (Auth)
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('is_superuser', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('role', sa.String(50), server_default='operator', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes for users
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Create access_logs table (Auth)
    op.create_table('access_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('accessed_fields', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for access_logs
    op.create_index('idx_access_logs_user', 'access_logs', ['user_id'])
    op.create_index('idx_access_logs_action', 'access_logs', ['action'])
    op.create_index('idx_access_logs_created', 'access_logs', ['created_at'])
    
    # Create customer_access table (Auth)
    op.create_table('customer_access',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_level', sa.String(20), server_default='masked', nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create indexes for customer_access
    op.create_index('idx_customer_access_customer', 'customer_access', ['customer_id'])
    op.create_index('idx_customer_access_user', 'customer_access', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('customer_access')
    op.drop_table('access_logs')
    op.drop_table('users')
    op.drop_table('settlement_records')
    op.drop_table('price_configs')
    op.drop_table('customers')
