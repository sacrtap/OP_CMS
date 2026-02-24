"""Add tiered pricing calculation support - Story 2.3

Revision ID: 004_tiered_pricing
Revises: 003_price_tiers
Create Date: 2026-02-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '004_tiered_pricing'
down_revision = '003_price_tiers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add calculation_type field to price_configs for tiered pricing
    op.add_column('price_configs',
        sa.Column('calculation_type', sa.String(20), nullable=True, server_default='progressive',
                  comment='Calculation type: progressive (累进) or flat (固定)')
    )
    
    # Add index for calculation_type
    op.create_index('idx_price_config_calc_type', 'price_configs', ['calculation_type'])
    
    # Add check constraint for calculation_type values
    # Note: MySQL check constraints are parsed but not enforced in older versions


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_price_config_calc_type', table_name='price_configs')
    
    # Drop column
    op.drop_column('price_configs', 'calculation_type')
