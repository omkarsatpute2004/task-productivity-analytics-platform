"""Initial migration creating users, categories, tasks, and task_activity tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-10 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = sa.Enum('ADMIN', 'USER', name='user_role_enum')
    task_priority_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='task_priority_enum')
    task_status_enum = sa.Enum('TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='task_status_enum')
    activity_type_enum = sa.Enum(
        'TASK_CREATED', 'TASK_UPDATED', 'STATUS_CHANGED',
        'PRIORITY_CHANGED', 'DEADLINE_CHANGED', 'TASK_COMPLETED', 'TASK_DELETED',
        name='activity_type_enum'
    )

    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='USER'),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('priority', task_priority_enum, nullable=False, server_default='MEDIUM'),
        sa.Column('status', task_status_enum, nullable=False, server_default='TODO'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_hours', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('actual_hours', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.CheckConstraint('estimated_hours >= 0', name='check_estimated_hours_non_negative'),
        sa.CheckConstraint('actual_hours IS NULL OR actual_hours >= 0', name='check_actual_hours_non_negative'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_category_id', 'tasks', ['category_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_deadline', 'tasks', ['deadline'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('ix_tasks_completed_at', 'tasks', ['completed_at'])

    # 4. task_activity table
    op.create_table(
        'task_activity',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', activity_type_enum, nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_activity_task_id', 'task_activity', ['task_id'])
    op.create_index('ix_task_activity_user_id', 'task_activity', ['user_id'])
    op.create_index('ix_task_activity_created_at', 'task_activity', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_task_activity_created_at', table_name='task_activity')
    op.drop_index('ix_task_activity_user_id', table_name='task_activity')
    op.drop_index('ix_task_activity_task_id', table_name='task_activity')
    op.drop_table('task_activity')

    op.drop_index('ix_tasks_completed_at', table_name='tasks')
    op.drop_index('ix_tasks_created_at', table_name='tasks')
    op.drop_index('ix_tasks_deadline', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_category_id', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')

    op.drop_table('categories')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    op.execute('DROP TYPE IF EXISTS activity_type_enum')
    op.execute('DROP TYPE IF EXISTS task_status_enum')
    op.execute('DROP TYPE IF EXISTS task_priority_enum')
    op.execute('DROP TYPE IF EXISTS user_role_enum')
