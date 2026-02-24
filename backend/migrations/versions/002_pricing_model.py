"""Add pricing model fields to price_configs - Story 2.1

Revision ID: 002_pricing_model
Revises: 001_initial
Create Date: 2026-02-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002_pricing_model'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to price_configs table
    op.add_column('price_configs', 
        sa.Column('price_model', sa.String(20), nullable=False, server_default='single',
                  comment='Pricing model: single (单层), multi (多层), tiered (阶梯)')
    )
    
    op.add_column('price_configs',
        sa.Column('device_series', sa.String(10), nullable=False, server_default='X',
                  comment='Device series: X, N, L')
    )
    
    op.add_column('price_configs',
        sa.Column('unit_price', sa.DECIMAL(12, 4), nullable=False,
                  comment='Unit price for single-tier pricing')
    )
    
    # Add unique constraint for customer + device_series combination
    op.create_unique_constraint('unique_customer_device', 'price_configs', ['customer_id', 'device_series'])
    
    # Create indexes for new columns
    op.create_index('idx_price_config_model', 'price_configs', ['price_model'])
    op.create_index('idx_price_config_series', 'price_configs', ['device_series'])
    op.create_index('idx_price_config_unit_price', 'price_configs', ['unit_price'])
    
    # Add check constraint for device_series values (X, N, L)
    # Note: MySQL check constraints are parsed but not enforced in older versions
    # For production, consider using triggers or application-level validation


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_price_config_unit_price', table_name='price_configs')
    op.drop_index('idx_price_config_series', table_name='price_configs')
    op.drop_index('idx_price_config_model', table_name='price_configs')
    
    # Drop unique constraint
    op.drop_constraint('unique_customer_device', 'price_configs', type_='unique')
    
    # Drop columns
    op.drop_column('price_configs', 'unit_price')
    op.drop_column('price_configs', 'device_series')
    op.drop_column('price_configs', 'price_model')
