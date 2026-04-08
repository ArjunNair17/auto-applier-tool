"""initial

Revision ID: 001
Revises:
Create Date: 2025-04-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables."""
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('linkedin', sa.String(500), nullable=True),
        sa.Column('github', sa.String(500), nullable=True),
        sa.Column('portfolio', sa.String(500), nullable=True),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('work_authorization', sa.String(255), nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create job_batches table
    op.create_table(
        'job_batches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('imported_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=True),
    )

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('job_url', sa.Text(), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('resume_path', sa.String(500), nullable=True),
        sa.Column('ats_type', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('application_url', sa.String(1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('intervention_reason', sa.String(500), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create run_sessions table
    op.create_table(
        'run_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('stats_json', sa.Text(), nullable=True),
    )

    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=False),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('settings')
    op.drop_table('run_sessions')
    op.drop_table('applications')
    op.drop_table('jobs')
    op.drop_table('job_batches')
    op.drop_table('profiles')
