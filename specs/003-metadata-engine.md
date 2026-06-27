# Specification: 003 - Metadata Engine

## Overview
This specification details the Metadata Engine of ImpactGraph. The engine is responsible for parsing raw SQL view definitions into structured lineage dependencies, detecting schema drift (changes over time), and maintaining the active in-memory graph cache.

---

## Problem Statement
A data warehouse contains thousands of tables and views, but their relationships are hidden inside SQL queries and view definitions. To perform impact analysis, we need a processing engine that parses SQL statements, maps column-level dependencies, tracks modifications to schemas over time, and stores this graph structure in a high-performance format.

---

## Goals
*   Parse SQL `CREATE VIEW` statements to extract upstream source tables and columns.
*   Resolve fully qualified identifiers (e.g., `DB.SCHEMA.TABLE`) to database records.
*   Implement schema drift detection (log column additions, removals, or type changes).
*   Build a table-to-table and column-to-column dependency model.
*   Load and cache database dependencies into an in-memory `NetworkX` directed graph.

---

## User Stories
1.  **As an Analytics Engineer**, I want to create a view that joins three tables and see the column-level lineage populated automatically without manual tagging.
2.  **As a Data Governance Lead**, I want to receive an alert if a downstream column's data type changes from integer to string so I can audit potential reports breakage.
3.  **As a Platform Operator**, I want to query the shortest lineage path between two tables instantly without waiting for recursive database joins.

---

## Functional Requirements
*   **FR-1:** SQL Parsing: Parse view DDL queries using Python's `sqlglot` library to extract sources (`FROM`, `JOIN` expressions) and mappings (`SELECT` column aliases).
*   **FR-2:** Name Resolution: Resolve partial identifiers (e.g., `customers` referenced inside a view in schema `sales`) to their fully qualified database records (`prod_db.sales.customers`).
*   **FR-3:** Column Lineage Mapping: For each select expression in a view, insert a column-level edge record in the `dependencies` table linking the source column to the target view column.
*   **FR-4:** Schema Drift Detection: During sync, compare incoming columns against existing rows. If a column is missing, mark it as `is_deleted = TRUE` and log a `schema_history` entry. If a data type changes, write a modification log.
*   **FR-5:** Graph Caching: At startup, populate an in-memory `networkx.DiGraph` representing tables (nodes) and dependencies (edges). Provide helper functions to add, update, and remove nodes dynamically.

---

## UI Requirements
*   **Schema History Tab:** A timeline component displayed on the table details page. Lists historical schema mutations (e.g., *"Column email was added on 2026-06-25"*, *"Data type of price changed from INT to FLOAT"*).
*   **Drift Alert Board:** A global dashboard panel showing recent schema drift incidents across the warehouse, sortable by detection date.

---

## Backend Requirements
*   **SQL Parser:** `sqlglot` library for AST (Abstract Syntax Tree) traversal.
*   **Graph Processing:** `networkx` library to store DAG state and calculate paths.
*   **Domain Service:** `MetadataService` orchestrating parsing and upserting logic.

---

## Database Changes
We must track schema changes by adding a `schema_history` table:

```sql
CREATE TABLE schema_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES tables(id),
    column_id UUID REFERENCES columns(id),
    change_type VARCHAR(50) NOT NULL, -- 'COLUMN_ADDED', 'COLUMN_REMOVED', 'TYPE_MODIFIED'
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_job_id UUID REFERENCES sync_jobs(id)
);
```

---

## API Endpoints

### 1. Schema Drift Inquiries
*   `GET /api/v1/metadata/drift`
    *   **Description:** Get list of recent schema drift incidents.
    *   **Response (200 OK):** `[{"id": "uuid", "table_name": "FACT_ORDERS", "change_type": "COLUMN_REMOVED", "old_value": "SHIPPING_COST"}]`

### 2. Object Schema History
*   `GET /api/v1/metadata/tables/{id}/history`
    *   **Description:** Get timeline of changes for a specific table.
    *   **Response (200 OK):** `[{"detected_at": "timestamp", "change_type": "COLUMN_ADDED", "new_value": "DISCOUNT"}]`

---

## SQL parsing Logic Example (sqlglot)
When parsing a view query:
```sql
CREATE VIEW prod.sales.customer_summary AS 
SELECT c.cust_id, c.name, count(o.order_id) AS total_orders 
FROM prod.raw.customers c 
JOIN prod.raw.orders o ON c.cust_id = o.cust_id 
GROUP BY c.cust_id, c.name;
```
The parsing logic must:
1.  Identify source tables: `prod.raw.customers` and `prod.raw.orders`.
2.  Extract column mappings:
    *   `customer_summary.cust_id` ➔ `customers.cust_id`
    *   `customer_summary.name` ➔ `customers.name`
    *   `customer_summary.total_orders` ➔ `orders.order_id` (aggregation)
3.  Write these edges to the `dependencies` database table.

---

## Acceptance Criteria
1.  Parsing a view with multiple subqueries and table joins successfully extracts and persists all column-level dependencies.
2.  Renaming a column in Snowflake and running a sync triggers:
    *   One `COLUMN_REMOVED` drift entry (marking old column `is_deleted = TRUE`).
    *   One `COLUMN_ADDED` drift entry (inserting new column).
3.  FastAPI startup completes without error, and logs verify that the NetworkX graph cache was successfully populated with nodes.
4.  Circular view references (if any exist) do not crash the parser; the engine logs an error and skips invalid edges.

---

## Out of Scope
*   Parsing stored procedures or Javascript UDFs.
*   Data profiling (min, max, mean calculations).

---

## Future Enhancements
*   Adding support for column renames using lexical similarity matching (preventing delete+add loops).
*   Automatic column-level PII tagging propagation.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 002 - Snowflake Connector
