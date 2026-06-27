"""Initial schema creation

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-06-27 18:00:00.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from passlib.hash import bcrypt

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. Create databases table
    op.create_table(
        'databases',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('connection_config', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_databases_name'), 'databases', ['name'], unique=True)

    # 3. Create schemas table
    op.create_table(
        'schemas',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('database_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['database_id'], ['databases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create tables table
    op.create_table(
        'tables',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('schema_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('byte_size', sa.Integer(), nullable=True),
        sa.Column('owner', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['schema_id'], ['schemas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tables_name'), 'tables', ['name'], unique=False)

    # 5. Create columns table
    op.create_table(
        'columns',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('table_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('data_type', sa.String(length=100), nullable=False),
        sa.Column('is_nullable', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_columns_name'), 'columns', ['name'], unique=False)

    # 6. Create dependencies table
    op.create_table(
        'dependencies',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('upstream_table_id', UUID(as_uuid=True), nullable=False),
        sa.Column('downstream_table_id', UUID(as_uuid=True), nullable=False),
        sa.Column('upstream_column_id', UUID(as_uuid=True), nullable=True),
        sa.Column('downstream_column_id', UUID(as_uuid=True), nullable=True),
        sa.Column('dependency_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['upstream_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['downstream_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['upstream_column_id'], ['columns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['downstream_column_id'], ['columns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Create roles table
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('database_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['database_id'], ['databases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=False)

    # 8. Create role_inheritance association table
    op.create_table(
        'role_inheritance',
        sa.Column('parent_role_id', UUID(as_uuid=True), nullable=False),
        sa.Column('child_role_id', UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['parent_role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['child_role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('parent_role_id', 'child_role_id')
    )

    # 9. Create user_roles association table
    op.create_table(
        'user_roles',
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # 10. Create privileges table
    op.create_table(
        'privileges',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', UUID(as_uuid=True), nullable=False),
        sa.Column('privilege_type', sa.String(length=50), nullable=False),
        sa.Column('target_object_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_object_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. Create sync_jobs table
    op.create_table(
        'sync_jobs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('database_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('records_synced', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_logs', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['database_id'], ['databases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. Create schema_history table
    op.create_table(
        'schema_history',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('table_id', UUID(as_uuid=True), nullable=False),
        sa.Column('column_id', UUID(as_uuid=True), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.String(length=255), nullable=True),
        sa.Column('new_value', sa.String(length=255), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('sync_job_id', UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['column_id'], ['columns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sync_job_id'], ['sync_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. Create risk_scores table
    op.create_table(
        'risk_scores',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('table_id', UUID(as_uuid=True), nullable=False),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('is_dead', sa.Boolean(), nullable=False),
        sa.Column('missing_owner', sa.Boolean(), nullable=False),
        sa.Column('recommendations_json', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_id')
    )

    # --- SEED DATA ---
    # Create the default admin account: username 'admin', password 'password123'
    admin_id = str(uuid.uuid4())
    hashed_pwd = bcrypt.hash("password123")
    
    op.execute(
        f"INSERT INTO users (id, username, hashed_password) "
        f"VALUES ('{admin_id}', 'admin', '{hashed_pwd}')"
    )


def downgrade() -> None:
    op.drop_table('risk_scores')
    op.drop_table('schema_history')
    op.drop_table('sync_jobs')
    op.drop_table('privileges')
    op.drop_table('user_roles')
    op.drop_table('role_inheritance')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('dependencies')
    op.drop_index(op.f('ix_columns_name'), table_name='columns')
    op.drop_table('columns')
    op.drop_index(op.f('ix_tables_name'), table_name='tables')
    op.drop_table('tables')
    op.drop_table('schemas')
    op.drop_index(op.f('ix_databases_name'), table_name='databases')
    op.drop_table('databases')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
