import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, ForeignKey, Text, Table as SqlTable
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

# Association Table for Role Inheritance (Self-referential Many-to-Many)
role_inheritance = SqlTable(
    "role_inheritance",
    Base.metadata,
    Column("parent_role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("child_role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for User Roles (Many-to-Many User to Role)
user_roles = SqlTable(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Database(Base):
    __tablename__ = "databases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=False) # e.g. 'snowflake'
    connection_config = Column(Text, nullable=False) # AES-256 encrypted string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    schemas = relationship("Schema", back_populates="database", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="database", cascade="all, delete-orphan")
    sync_jobs = relationship("SyncJob", back_populates="database", cascade="all, delete-orphan")

class Schema(Base):
    __tablename__ = "schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_id = Column(UUID(as_uuid=True), ForeignKey("databases.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    database = relationship("Database", back_populates="schemas")
    tables = relationship("Table", back_populates="schema", cascade="all, delete-orphan")

class Table(Base):
    __tablename__ = "tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("schemas.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False) # 'BASE TABLE', 'VIEW', etc.
    row_count = Column(Integer, nullable=True)
    byte_size = Column(Integer, nullable=True)
    owner = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    schema = relationship("Schema", back_populates="tables")
    columns = relationship("ColumnModel", back_populates="table", cascade="all, delete-orphan")
    risk_score = relationship("RiskScore", uselist=False, back_populates="table", cascade="all, delete-orphan")
    schema_histories = relationship("SchemaHistory", back_populates="table", cascade="all, delete-orphan")

class ColumnModel(Base):
    __tablename__ = "columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    data_type = Column(String(100), nullable=False)
    is_nullable = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    table = relationship("Table", back_populates="columns")

class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False) # 'table_to_table', 'column_to_column'
    
    # Table edges
    upstream_table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    downstream_table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    
    # Column edges (Nullable)
    upstream_column_id = Column(UUID(as_uuid=True), ForeignKey("columns.id", ondelete="CASCADE"), nullable=True)
    downstream_column_id = Column(UUID(as_uuid=True), ForeignKey("columns.id", ondelete="CASCADE"), nullable=True)
    
    dependency_type = Column(String(50), nullable=False) # 'view_definition', 'foreign_key'

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_id = Column(UUID(as_uuid=True), ForeignKey("databases.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)

    # Relationships
    database = relationship("Database", back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    parents = relationship(
        "Role",
        secondary=role_inheritance,
        primaryjoin=(id == role_inheritance.c.child_role_id),
        secondaryjoin=(id == role_inheritance.c.parent_role_id),
        backref="children"
    )

class Privilege(Base):
    __tablename__ = "privileges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    privilege_type = Column(String(50), nullable=False) # 'SELECT', 'INSERT', 'OWNERSHIP'
    target_object_id = Column(UUID(as_uuid=True), nullable=False) # Polymorphic UUID reference
    target_object_type = Column(String(50), nullable=False) # 'TABLE', 'SCHEMA', 'DATABASE'

class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_id = Column(UUID(as_uuid=True), ForeignKey("databases.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False) # 'RUNNING', 'SUCCESS', 'FAILED'
    records_synced = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    execution_logs = Column(Text, nullable=True)

    # Relationships
    database = relationship("Database", back_populates="sync_jobs")
    schema_histories = relationship("SchemaHistory", back_populates="sync_job", cascade="all, delete-orphan")

class SchemaHistory(Base):
    __tablename__ = "schema_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    column_id = Column(UUID(as_uuid=True), ForeignKey("columns.id", ondelete="SET NULL"), nullable=True)
    change_type = Column(String(50), nullable=False) # 'COLUMN_ADDED', 'COLUMN_REMOVED', 'TYPE_MODIFIED'
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    sync_job_id = Column(UUID(as_uuid=True), ForeignKey("sync_jobs.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    table = relationship("Table", back_populates="schema_histories")
    sync_job = relationship("SyncJob", back_populates="schema_histories")

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), unique=True, nullable=False)
    composite_score = Column(Float, default=0.0, nullable=False)
    is_dead = Column(Boolean, default=False, nullable=False)
    missing_owner = Column(Boolean, default=False, nullable=False)
    recommendations_json = Column(Text, nullable=True) # Serialized list of warnings
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    table = relationship("Table", back_populates="risk_score")
