import json
import logging
import snowflake.connector
from typing import Dict, Any, List
from app.core.encrypt import decrypt_data

logger = logging.getLogger(__name__)

class SnowflakeClient:
    def __init__(self, connection_config_encrypted: str):
        """
        Decrypt connection credentials and initialize Snowflake client variables.
        """
        try:
            decrypted_str = decrypt_data(connection_config_encrypted)
            self.config = json.loads(decrypted_str)
        except Exception as e:
            logger.error(f"Failed to decrypt Snowflake credentials: {str(e)}")
            raise ValueError("Invalid connection credentials payload.")

        self.account = self.config.get("account")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.warehouse = self.config.get("warehouse")
        self.database = self.config.get("database") # Default database to scan
        self.schema = self.config.get("schema", "PUBLIC")

    def _get_connection(self):
        """Establish a direct session connection to Snowflake."""
        return snowflake.connector.connect(
            user=self.username,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )

    def test_connection(self) -> bool:
        """Verify credentials connection and run a simple select probe query."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Snowflake connection handshake failed: {str(e)}")
            raise e
        finally:
            if conn:
                conn.close()

    def fetch_schemas(self, database_name: str) -> List[str]:
        """Fetch all visible non-information_schema schemas inside a database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {database_name}")
            schemas = []
            for row in cursor.fetchall():
                # Columns: created_on, name, is_default, is_current, database_name, owner, comment, options
                schema_name = row[1]
                if schema_name != "INFORMATION_SCHEMA":
                    schemas.append(schema_name)
            return schemas
        finally:
            conn.close()

    def fetch_tables_and_views(self, database_name: str) -> List[Dict[str, Any]]:
        """Fetch all tables and views metadata in a database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT 
                    table_schema, 
                    table_name, 
                    table_type, 
                    row_count, 
                    bytes, 
                    comment 
                FROM {database_name}.INFORMATION_SCHEMA.TABLES
                WHERE table_schema != 'INFORMATION_SCHEMA'
            """
            cursor.execute(query)
            items = []
            for row in cursor.fetchall():
                items.append({
                    "schema": row[0],
                    "name": row[1],
                    "type": row[2], # 'BASE TABLE' or 'VIEW'
                    "row_count": row[3],
                    "byte_size": row[4],
                    "description": row[5] or ""
                })
            return items
        finally:
            conn.close()

    def fetch_columns(self, database_name: str) -> List[Dict[str, Any]]:
        """Fetch all columns metadata in a database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT 
                    table_schema, 
                    table_name, 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    comment 
                FROM {database_name}.INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema != 'INFORMATION_SCHEMA'
                ORDER BY ordinal_position
            """
            cursor.execute(query)
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "schema": row[0],
                    "table_name": row[1],
                    "name": row[2],
                    "data_type": row[3],
                    "is_nullable": row[4] == 'YES',
                    "description": row[5] or ""
                })
            return columns
        finally:
            conn.close()

    def fetch_view_ddl(self, database_name: str, schema_name: str, view_name: str) -> str:
        """Fetch the DDL statement defining a specific view."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # GET_DDL returns the CREATE VIEW ... statement
            cursor.execute(f"SELECT GET_DDL('VIEW', '{database_name}.{schema_name}.{view_name}')")
            row = cursor.fetchone()
            return row[0] if row else ""
        except Exception as e:
            logger.warning(f"Failed to fetch DDL for view {schema_name}.{view_name}: {str(e)}")
            return ""
        finally:
            conn.close()

    def fetch_roles(self) -> List[str]:
        """Fetch list of all roles configured in the Snowflake account."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW ROLES")
            roles = []
            for row in cursor.fetchall():
                # Columns: created_on, name, is_default, is_current, is_inherited, assigned_to_users, granted_to_roles, granted_roles, owner, comment
                role_name = row[1]
                roles.append(role_name)
            return roles
        except Exception as e:
            logger.error(f"Failed to fetch Snowflake roles: {str(e)}")
            return []
        finally:
            conn.close()

    def fetch_role_grants(self, role_name: str) -> List[Dict[str, Any]]:
        """Fetch all privilege grants assigned to a specific role."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SHOW GRANTS TO ROLE {role_name}")
            grants = []
            for row in cursor.fetchall():
                # Columns: created_on, privilege, granted_on, name, granted_to, grantee_name, grant_option, granted_by
                grants.append({
                    "privilege": row[1],
                    "target_type": row[2], # 'DATABASE', 'SCHEMA', 'TABLE', 'ROLE' etc.
                    "target_name": row[3], # Name of the target object
                    "granted_to": row[4],
                    "grantee_name": row[5],
                })
            return grants
        except Exception as e:
            logger.warning(f"Failed to fetch grants for role {role_name}: {str(e)}")
            return []
        finally:
            conn.close()
