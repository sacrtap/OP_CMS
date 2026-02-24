"""Add price config version control - Story 2.4

Revision ID: 005_version_control
Revises: 004_tiered_pricing
Create Date: 2026-03-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005_version_control'
down_revision = '004_tiered_pricing'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create price_config_versions table for version history
    op.create_table('price_config_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version_id', sa.String(36), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False, comment='Reference to current config'),
        sa.Column('version_number', sa.Integer(), nullable=False, comment='Version number (1, 2, 3...)'),
        
        # Snapshot of config data
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_model', sa.String(20), nullable=False),
        sa.Column('device_series', sa.String(10), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('pricing_rules', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        
        # Change tracking
        sa.Column('changed_by', sa.Integer(), nullable=True, comment='User ID who made the change'),
        sa.Column('change_reason', sa.String(500), nullable=True, comment='Reason for this version'),
        sa.Column('changes_summary', sa.JSON(), nullable=True, comment='JSON of changed fields'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id'),
        sa.ForeignKeyConstraint(['config_id'], ['price_configs.id'], ondelete='CASCADE'),
        sa.Index('idx_version_config', 'config_id'),
        sa.Index('idx_version_number', 'version_number'),
        sa.Index('idx_version_config_number', 'config_id', 'version_number')
    )
    
    # Add current_version_number to price_configs for quick access
    op.add_column('price_configs',
        sa.Column('current_version_number', sa.Integer(), nullable=True, server_default='1',
                  comment='Current version number')
    )
    
    op.create_index('idx_price_config_version', 'price_configs', ['current_version_number'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_price_config_version', table_name='price_configs')
    
    # Drop column
    op.drop_column('price_configs', 'current_version_number')
    
    # Drop table
    op.drop_table('price_config_versions')
