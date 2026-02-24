"""Add price tiers table for multi-tier pricing - Story 2.2

Revision ID: 003_price_tiers
Revises: 002_pricing_model
Create Date: 2026-02-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003_price_tiers'
down_revision = '002_pricing_model'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create price_tiers table for multi-tier pricing
    op.create_table('price_tiers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tier_id', sa.String(36), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('tier_level', sa.Integer(), nullable=False, comment='Tier level (1, 2, 3...)'),
        sa.Column('min_quantity', sa.DECIMAL(10, 2), nullable=False, comment='Minimum quantity for this tier'),
        sa.Column('max_quantity', sa.DECIMAL(10, 2), nullable=True, comment='Maximum quantity for this tier (NULL for last tier)'),
        sa.Column('unit_price', sa.DECIMAL(12, 4), nullable=False, comment='Unit price for this tier'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tier_id'),
        sa.ForeignKeyConstraint(['config_id'], ['price_configs.id'], ondelete='CASCADE'),
        sa.CheckConstraint('min_quantity >= 0', name='check_min_quantity_non_negative'),
        sa.CheckConstraint('max_quantity IS NULL OR max_quantity > min_quantity', name='check_max_greater_than_min')
    )
    
    # Create indexes
    op.create_index('idx_price_tiers_config', 'price_tiers', ['config_id'])
    op.create_index('idx_price_tiers_level', 'price_tiers', ['tier_level'])
    op.create_index('idx_price_tiers_config_level', 'price_tiers', ['config_id', 'tier_level'])
    
    # Add price_model field validation comment
    op.create_index('idx_price_config_active', 'price_configs', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_price_config_active', table_name='price_configs')
    op.drop_index('idx_price_tiers_config_level', table_name='price_tiers')
    op.drop_index('idx_price_tiers_level', table_name='price_tiers')
    op.drop_index('idx_price_tiers_config', table_name='price_tiers')
    
    # Drop table
    op.drop_table('price_tiers')
