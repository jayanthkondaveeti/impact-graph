import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import (
    Database, Schema, Table, ColumnModel, Role, Privilege, 
    SyncJob, SchemaHistory, role_inheritance, user_roles
)
from app.core.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)

class SyncService:
    @staticmethod
    def run_sync(db: Session, database_id: str) -> str:
        """
        Run database metadata synchronization from Snowflake to PostgreSQL.
        Returns the created SyncJob ID.
        """
        # 1. Fetch connection details
        db_config = db.query(Database).filter(Database.id == database_id).first()
        if not db_config:
            raise ValueError(f"Database connection profile with ID {database_id} not found.")

        # 2. Create and start a SyncJob tracking record
        job = SyncJob(
            database_id=database_id,
            status="RUNNING",
            started_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            # 3. Instantiate Snowflake Client
            client = SnowflakeClient(db_config.connection_config)
            
            # Use the default database name specified in settings
            database_name = client.database
            if not database_name:
                raise ValueError("No target database specified in connection configuration.")

            records_synced_count = 0
            
            # --- SCHEMA CRAWL ---
            schemas_list = client.fetch_schemas(database_name)
            tables_and_views = client.fetch_tables_and_views(database_name)
            columns_list = client.fetch_columns(database_name)

            # Keep track of active schema IDs to delete missing ones
            active_schema_ids = set()
            active_table_ids = set()
            active_column_ids = set()

            # Process Schemas
            schema_map = {} # Maps schema name -> Schema database model ID
            for schema_name in schemas_list:
                schema_record = db.query(Schema).filter(
                    Schema.database_id == database_id,
                    Schema.name == schema_name
                ).first()
                
                if not schema_record:
                    schema_record = Schema(
                        database_id=database_id,
                        name=schema_name
                    )
                    db.add(schema_record)
                    db.flush()
                
                schema_map[schema_name] = schema_record.id
                active_schema_ids.add(schema_record.id)

            # Process Tables and Views
            # Index table configurations by schema + name
            table_records_map = {}
            for item in tables_and_views:
                schema_name = item["schema"]
                schema_id = schema_map.get(schema_name)
                if not schema_id:
                    continue # Skip schemas that are not crawled
                    
                table_name = item["name"]
                table_type = item["type"]
                row_count = item["row_count"]
                byte_size = item["byte_size"]
                description = item["description"]
                
                # Fetch view DDL if it is a view
                view_definition = None
                if table_type == "VIEW":
                    view_definition = client.fetch_view_ddl(database_name, schema_name, table_name)

                table_record = db.query(Table).filter(
                    Table.schema_id == schema_id,
                    Table.name == table_name
                ).first()

                if not table_record:
                    table_record = Table(
                        schema_id=schema_id,
                        name=table_name,
                        type=table_type,
                        row_count=row_count,
                        byte_size=byte_size,
                        description=view_definition or description, # Store DDL for views
                        is_deleted=False
                    )
                    db.add(table_record)
                    db.flush()
                else:
                    # Update metrics if changed
                    table_record.row_count = row_count
                    table_record.byte_size = byte_size
                    table_record.is_deleted = False
                    if view_definition:
                        table_record.description = view_definition
                    db.add(table_record)
                
                table_records_map[(schema_name, table_name)] = table_record
                active_table_ids.add(table_record.id)
                records_synced_count += 1

            # Process Columns
            # Group columns by table key
            columns_by_table = {}
            for col in columns_list:
                key = (col["schema"], col["table_name"])
                if key not in columns_by_table:
                    columns_by_table[key] = []
                columns_by_table[key].append(col)

            for key, cols in columns_by_table.items():
                table_record = table_records_map.get(key)
                if not table_record:
                    continue
                    
                for col in cols:
                    col_name = col["name"]
                    data_type = col["data_type"]
                    is_nullable = col["is_nullable"]
                    description = col["description"]

                    col_record = db.query(ColumnModel).filter(
                        ColumnModel.table_id == table_record.id,
                        ColumnModel.name == col_name
                    ).first()

                    if not col_record:
                        col_record = ColumnModel(
                            table_id=table_record.id,
                            name=col_name,
                            data_type=data_type,
                            is_nullable=is_nullable,
                            description=description,
                            is_deleted=False
                        )
                        db.add(col_record)
                        db.flush()

                        # Audit schema history: column added
                        history = SchemaHistory(
                            table_id=table_record.id,
                            column_id=col_record.id,
                            change_type="COLUMN_ADDED",
                            new_value=f"{col_name} ({data_type})",
                            sync_job_id=job.id
                        )
                        db.add(history)
                    else:
                        # Check if data type modified
                        if col_record.data_type != data_type:
                            history = SchemaHistory(
                                table_id=table_record.id,
                                column_id=col_record.id,
                                change_type="TYPE_MODIFIED",
                                old_value=col_record.data_type,
                                new_value=data_type,
                                sync_job_id=job.id
                            )
                            db.add(history)
                            col_record.data_type = data_type
                            
                        col_record.is_deleted = False
                        db.add(col_record)

                    active_column_ids.add(col_record.id)
                    records_synced_count += 1

            # Soft-delete tables that are no longer present in Snowflake
            tables_to_delete = db.query(Table).join(Schema).filter(
                Schema.database_id == database_id,
                Table.is_deleted == False,
                ~Table.id.in_(list(active_table_ids))
            ).all()
            for t in tables_to_delete:
                t.is_deleted = True
                db.add(t)

            # Soft-delete columns of active tables that were removed
            columns_to_delete = db.query(ColumnModel).join(Table).join(Schema).filter(
                Schema.database_id == database_id,
                ColumnModel.is_deleted == False,
                ~ColumnModel.id.in_(list(active_column_ids))
            ).all()
            for c in columns_to_delete:
                c.is_deleted = True
                db.add(c)
                # Audit schema history: column removed
                history = SchemaHistory(
                    table_id=c.table_id,
                    column_id=c.id,
                    change_type="COLUMN_REMOVED",
                    old_value=f"{c.name} ({c.data_type})",
                    sync_job_id=job.id
                )
                db.add(history)

            # --- SECURITY & ROLES CRAWL ---
            roles_list = client.fetch_roles()
            role_records_map = {} # Maps name -> Role DB model

            # Delete old privileges/inheritance for clean rebuild
            db.query(Privilege).filter(
                Privilege.role_id.in_(
                    db.query(Role.id).filter(Role.database_id == database_id)
                )
            ).delete(synchronize_session=False)

            db.execute(role_inheritance.delete().where(
                role_inheritance.c.parent_role_id.in_(
                    db.query(Role.id).filter(Role.database_id == database_id)
                )
            ))

            for role_name in roles_list:
                role_record = db.query(Role).filter(
                    Role.database_id == database_id,
                    Role.name == role_name
                ).first()

                if not role_record:
                    role_record = Role(
                        database_id=database_id,
                        name=role_name
                    )
                    db.add(role_record)
                    db.flush()
                
                role_records_map[role_name] = role_record

            # Fetch grants for each role to build privileges and inheritance trees
            for role_name, role_record in role_records_map.items():
                grants = client.fetch_role_grants(role_name)
                for grant in grants:
                    priv_type = grant["privilege"]
                    target_type = grant["target_type"]
                    target_name = grant["target_name"]
                    
                    if target_type == "ROLE":
                        # Set up Role Inheritance: B is granted to A (meaning A inherits B)
                        parent_role = role_records_map.get(target_name)
                        child_role = role_record # A
                        if parent_role and child_role:
                            db.execute(
                                role_inheritance.insert().values(
                                    parent_role_id=parent_role.id,
                                    child_role_id=child_role.id
                                )
                            )
                    elif target_type in ["DATABASE", "SCHEMA", "TABLE"]:
                        # Resolve database target IDs if possible
                        target_object_id = None
                        if target_type == "DATABASE" and target_name == database_name:
                            target_object_id = database_id
                        elif target_type == "SCHEMA":
                            # Target name structure: DB.SCHEMA or SCHEMA
                            clean_schema_name = target_name.split('.')[-1]
                            schema_rec = db.query(Schema).filter(
                                Schema.database_id == database_id,
                                Schema.name == clean_schema_name
                            ).first()
                            if schema_rec:
                                target_object_id = schema_rec.id
                        elif target_type == "TABLE":
                            # Target name structure: DB.SCHEMA.TABLE
                            tokens = target_name.split('.')
                            if len(tokens) >= 3:
                                clean_schema_name = tokens[-2]
                                clean_table_name = tokens[-1]
                                table_rec = db.query(Table).join(Schema).filter(
                                    Schema.database_id == database_id,
                                    Schema.name == clean_schema_name,
                                    Table.name == clean_table_name
                                ).first()
                                if table_rec:
                                    target_object_id = table_rec.id

                        if target_object_id:
                            privilege = Privilege(
                                role_id=role_record.id,
                                privilege_type=priv_type,
                                target_object_id=target_object_id,
                                target_object_type=target_type
                            )
                            db.add(privilege)

            # 4. Finalize Sync Job status
            job.status = "SUCCESS"
            job.records_synced = records_synced_count
            job.completed_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()
            
            logger.info(f"SyncJob {job.id} completed successfully. Synced {records_synced_count} objects.")
            return str(job.id)

        except Exception as e:
            # 5. Handle failures cleanly
            db.rollback()
            logger.error(f"SyncJob {job.id} failed: {str(e)}")
            
            # Re-fetch session context to update job status
            job_failed = db.query(SyncJob).filter(SyncJob.id == job.id).first()
            if job_failed:
                job_failed.status = "FAILED"
                job_failed.completed_at = datetime.now(timezone.utc)
                job_failed.error_message = str(e)
                db.add(job_failed)
                db.commit()
            raise e
