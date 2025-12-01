"""Add device_tokens table

Revision ID: d24159fb95f6
Revises: 74f7ca8b76b3
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd24159fb95f6'
down_revision = '74f7ca8b76b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    # Only create table if it doesn't exist
    if 'device_tokens' not in tables:
        op.create_table('device_tokens',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('token', sa.String(), nullable=False),
            sa.Column('platform', sa.String(20), nullable=False),
            sa.Column('device_info', postgresql.JSONB(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'token', name='_user_token_uc')
        )
        op.create_index(op.f('ix_device_tokens_id'), 'device_tokens', ['id'], unique=False)
        op.create_index(op.f('ix_device_tokens_user_id'), 'device_tokens', ['user_id'], unique=False)
        op.create_index('idx_device_tokens_active', 'device_tokens', ['user_id', 'is_active'], 
                       postgresql_where=sa.text('is_active = true'))
        print("✅ Created device_tokens table")
    else:
        print("⏭️  Table device_tokens already exists, skipping creation")


def downgrade() -> None:
    op.drop_index('idx_device_tokens_active', table_name='device_tokens')
    op.drop_index(op.f('ix_device_tokens_user_id'), table_name='device_tokens')
    op.drop_index(op.f('ix_device_tokens_id'), table_name='device_tokens')
    op.drop_table('device_tokens')

