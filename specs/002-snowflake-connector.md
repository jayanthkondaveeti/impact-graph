# Specification: 002 - Snowflake Connector

## Overview
This specification details the Snowflake Connector plugin for ImpactGraph. The connector establishes secure communication with a Snowflake account, extracts schema metadata, fetches role permissions, and records synchronization job statuses.

---

## Problem Statement
Tracing data lineage and structural risk requires a complete record of data warehouses. We need an extraction pipeline that can connect securely to Snowflake (handling password and private-key authentication), retrieve table/view configurations and permissions without impacting database performance, and track sync execution history.

---

## Goals
*   Implement secure connection handshakes supporting both Username/Password and Private Key pair authentication.
*   Extract metadata schemas (Databases, Schemas, Tables, Views, Columns, and Data Types).
*   Retrieve SQL `CREATE VIEW` statements to enable downstream lineage parsing.
*   Capture RBAC mappings (Grants, Role Inheritance, and User memberships).
*   Create a background worker schedule using a cron syntax (e.g., midnight syncs).
*   Record execution history and diagnostic error codes for sync tasks.

---

## User Stories
1.  **As a Data Platform Engineer**, I want to authenticate to Snowflake using an encrypted keypair so my password is not stored.
2.  **As an Analytics Team Lead**, I want the metadata to synchronize every night at 2:00 AM so the lineage dashboard reflects the latest schema refactoring.
3.  **As a System Administrator**, I want to see a log of past sync jobs so I can diagnose if a sync failed due to Snowflake network timeouts.

---

## Functional Requirements
*   **FR-1:** Authentication Options: Must support password-based and encrypted private keypair-based connection handshakes using the standard `snowflake-connector-python` SDK.
*   **FR-2:** Ingestion Scope: Ingest database assets filtered by user-defined whitelist patterns (e.g., `prod_db.*, staging_db.public.*`).
*   **FR-3:** Metadata Extraction: Execute metadata queries against Snowflake's `INFORMATION_SCHEMA` or `ACCOUNT_USAGE` schemas to fetch tables, columns, and view definitions.
*   **FR-4:** Privilege Extraction: Retrieve list of grants, role hierarchies, and user mappings:
    *   `SHOW GRANTS ON TABLE <name>`
    *   `SHOW GRANTS TO ROLE <name>`
*   **FR-5:** Job Runner: Execute jobs asynchronously using a background scheduler (e.g., Python `APScheduler`).
*   **FR-6:** Incremental Sync: Compare object `LAST_ALTERED` dates against the last sync execution timestamp to only fetch altered metadata.

---

## UI Requirements
*   **Connection Wizard:** Fields to input credentials with an interactive "Test Connection" button that runs a lightweight query (`SELECT 1`).
*   **Sync Monitor Console:**
    *   Quick metrics: "Last Successful Sync", "Duration", "Tables Imported".
    *   An "Ingest Now" button to execute manual sync runs.
    *   History table listing job status (Success, Failed, Running), timestamps, and logs.

---

## Backend Requirements
*   **Driver:** `snowflake-connector-python` library.
*   **Key Decryption:** Load and decrypt encrypted PKCS#8 private keys using `cryptography.hazmat.primitives.serialization`.
*   **Scheduler:** `APScheduler` configured with SQLAlchemy job store to persist schedules in PostgreSQL.

---

## Database Changes
We must track sync history by adding a `sync_jobs` table:

```sql
CREATE TABLE sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID NOT NULL REFERENCES databases(id),
    status VARCHAR(50) NOT NULL, -- 'RUNNING', 'SUCCESS', 'FAILED'
    records_synced INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    execution_logs TEXT
);
```

---

## API Endpoints

### 1. Connection Verification
*   `POST /api/v1/connectors/test`
    *   **Description:** Validates connection details without persisting changes.
    *   **Request Body:** Connection credential object.
    *   **Response (200 OK):** `{"status": "success", "message": "Connection established successfully."}`

### 2. Job Control
*   `POST /api/v1/connectors/sync`
    *   **Description:** Enqueues a manual metadata sync job.
    *   **Request Body:** `{"database_id": "uuid"}`
    *   **Response (202 Accepted):** `{"job_id": "uuid", "status": "RUNNING"}`
*   `GET /api/v1/connectors/sync/history`
    *   **Description:** Get list of past sync job runs.
    *   **Response (200 OK):** `[{"id": "uuid", "status": "SUCCESS", "started_at": "timestamp"}]`

---

## Ingestion SQL Queries (Snowflake Targets)
To retrieve metadata efficiently without querying massive tables directly, the connector runs these database queries:

```sql
-- Retrieve Tables and Views
SELECT 
    table_catalog, table_schema, table_name, table_type, 
    row_count, bytes, comment, last_altered
FROM information_schema.tables 
WHERE table_schema != 'INFORMATION_SCHEMA';

-- Retrieve Columns
SELECT 
    table_catalog, table_schema, table_name, column_name, 
    data_type, is_nullable, comment
FROM information_schema.columns
WHERE table_schema != 'INFORMATION_SCHEMA';

-- Retrieve View DDL definitions
SELECT 
    table_catalog, table_schema, table_name, view_definition
FROM information_schema.views
WHERE table_schema != 'INFORMATION_SCHEMA';
```

---

## Acceptance Criteria
1.  Clicking "Test Connection" with incorrect Snowflake credentials returns a `400 Bad Request` containing clear, sanitized logs.
2.  Triggering a sync inserts databases, schemas, tables, and columns into Postgres, and creates a `sync_jobs` record with status `SUCCESS`.
3.  View definitions are correctly written to the `tables` record.
4.  Network drops or timeouts trigger 3 retries before setting the job status to `FAILED` and logging the trace stack.

---

## Out of Scope
*   Syncing other database platforms (Redshift, Databricks).
*   Extracting actual data records from tables (metadata only).

---

## Future Enhancements
*   Adding support for SSH tunneling / Bastion hosts.
*   Webhook integrations to trigger syncs after dbt execution runs.

---

## Dependencies
*   Spec 001 - Project Foundation (credentials storage & DB schema).
