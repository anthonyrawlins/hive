"""Add CLI agent support

Revision ID: 002_add_cli_agent_support
Revises: 001_initial_migration
Create Date: 2025-07-10 09:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_add_cli_agent_support'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    """Add CLI agent support columns to agents table"""
    # Add agent_type column with default 'ollama'
    op.add_column('agents', sa.Column('agent_type', sa.String(), nullable=False, server_default='ollama'))
    
    # Add cli_config column for CLI-specific configuration
    op.add_column('agents', sa.Column('cli_config', sa.JSON(), nullable=True))


def downgrade():
    """Remove CLI agent support columns"""
    op.drop_column('agents', 'cli_config')
    op.drop_column('agents', 'agent_type')