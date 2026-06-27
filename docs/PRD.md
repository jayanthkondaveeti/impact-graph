# Product Requirements Document (PRD): ImpactGraph MVP

## 1. Product Overview

ImpactGraph is an open-source Data Impact Analysis Platform. The platform connects to modern data platforms, extracts schemas, lineage, and privileges, and transforms them into a queryable dependency graph. This allows data teams to conduct change-impact analysis, trace access controls, audit structural risks, and answer critical operational questions before refactoring data assets.

---

## 2. Goals & Non-Goals

### Core MVP Goals
*   **Establish Snowflake Connectivity:** Authenticate securely and extract metadata (tables, views, columns, schemas, databases, and structural relationships).
*   **Generate Dependency Lineage:** Create accurate column-level and table-level lineage relationships by parsing view definitions and foreign keys.
*   **Enable Global Search:** Provide an intuitive search bar to find tables, views, columns, and databases by name, description, or tags.
*   **Compute Blast Radius & Impact Analysis:** Quantify the operational impact (downstream assets affected) of altering or deleting any given table/column.
*   **Visualize RBAC Hierarchies:** Map how roles, users, and privileges flow downward to specific data assets in Snowflake.
*   **Provide a Risk Scoring Engine:** Highlight critical schemas, dead views (views referencing deleted tables), and unmaintained/unowned tables.
*   **Deliver an Open-Source, Self-Hostable Package:** Enable deployment via Docker Compose with a single command.

### Non-Goals (Out of Scope for MVP)
*   **Multi-Tenant SaaS Management:** The MVP is a single-tenant instance deployed within an organization's secure network.
*   **Real-time Streaming Syncs:** Syncing runs as a scheduled batch job (cron) or on-demand, not in real-time.
*   **Non-Snowflake Warehouse Ingestion:** Support for BigQuery, Redshift, Databricks, or dbt is deferred to v1.1.
*   **BI Tool Metadata Integration:** Ingesting Tableau, Looker, or PowerBI dashboards is deferred to v1.1.
*   **In-line Write Actions:** ImpactGraph will not execute modification statements (e.g., `DROP TABLE`) on the target database. It is read-only.

---

## 3. User Personas & Scenarios

### Persona A: Marcus (Lead Data Platform Engineer)
*   **Objective:** Wants to clean up a legacy Snowflake database by dropping 50 tables marked as "temporary" or "deprecated" three years ago.
*   **Scenario:** Marcus searches for `TMP_CUSTOMER_RECORDS_2022`. ImpactGraph displays the object details page showing a **Blast Radius Score of 24** and lists 3 downstream staging views and 1 active executive dashboard that directly query it. Marcus decides not to delete it yet, avoiding a major pipeline failure.

### Persona B: Elena (Analytics Engineer)
*   **Objective:** Needs to modify the schema of the main `FACT_TRANSACTIONS` table (renaming `total_price` to `gross_amount`) to align with finance naming rules.
*   **Scenario:** Elena opens the lineage graph for `FACT_TRANSACTIONS.total_price`. She visually traces the column dependency downstream and lists the 8 views that select from it. She can systematically write migration scripts for those 8 views before releasing her changes.

### Persona C: Kenji (Security Compliance Auditor)
*   **Objective:** Audit who has access to the sensitive `CUSTOMER_SSN` column in the payroll schema.
*   **Scenario:** Kenji enters `CUSTOMER_SSN` in the global search. He selects the column and navigates to the **RBAC Explorer** tab. The UI renders the inheritance hierarchy: `ACCOUNTADMIN ➔ SECURITYADMIN ➔ FIN_LEAD ➔ FIN_ANALYST` showing exactly how the `FIN_ANALYST` role inherited the privilege to read this column.

---

## 4. Functional Requirements

### 4.1. Project Foundation & Configuration
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-1.1** | The application must launch via `docker-compose up` running PostgreSQL, Backend, and Frontend. | P0 |
| **FR-1.2** | Secure credential storage: database passwords/keys must be encrypted in Postgres using AES-256. | P0 |
| **FR-1.3** | Single-tenant, local password authentication for accessing the web portal. | P0 |

### 4.2. Snowflake Connector
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-2.1** | Support authentication via Username/Password and Private Key/Passphrase. | P0 |
| **FR-2.2** | Extract tables, views, materialised views, columns (names, types, nullability). | P0 |
| **FR-2.3** | Extract view definition SQL statements for lineage parsing. | P0 |
| **FR-2.4** | Extract grants, roles, role memberships, and user lists to construct the RBAC tree. | P0 |
| **FR-2.5** | Incremental metadata synchronization: only scan objects modified since the last sync. | P1 |
| **FR-2.6** | Allow triggering sync on-demand via UI button, or setting custom cron schedules. | P0 |

### 4.3. Metadata & Graph Engine
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-3.1** | Model Snowflake objects as nodes (Database, Schema, Table, Column, Role, User). | P0 |
| **FR-3.2** | Map relationship edges (contains, references, grants, inherits, member_of). | P0 |
| **FR-3.3** | Parse view SQL strings to build table-to-table and column-to-column lineage links. | P0 |
| **FR-3.4** | Detect "Dead Objects": views or tables referencing objects that no longer exist in the DB. | P0 |
| **FR-3.5** | Retain versioned snapshots of schemas to track changes over time (schema drift). | P1 |

### 4.4. Global Search & Explorer
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-4.1** | Global search box in the header with instant autocomplete. | P0 |
| **FR-4.2** | Filter search results by database, schema, object type (table vs view), and tags. | P0 |
| **FR-4.3** | Object details view showing schemas, descriptions, row count/size, tags, and owners. | P0 |

### 4.5. Lineage Graph Visualizer
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-5.1** | Render interactive lineage nodes (Tables/Views) and directional flow edges (left-to-right). | P0 |
| **FR-5.2** | Toggle between Table-level lineage and Column-level lineage views. | P0 |
| **FR-5.3** | Interactive canvas navigation (zoom, pan, drag-and-drop nodes). | P0 |
| **FR-5.4** | Highlight upstream and downstream paths upon clicking a specific node/column. | P0 |

### 4.6. Blast Radius & Change Impact
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-6.1** | Compute a "Blast Radius Score" (0-100) based on downstream dependencies and degree. | P0 |
| **FR-6.2** | List all downstream objects affected by a hypothetical delete action on the target node. | P0 |
| **FR-6.3** | Expose a `/api/v1/impact/blast-radius` endpoint for integrations (e.g., CI/CD bots). | P0 |

### 4.7. Governance & RBAC Explorer
| ID | Requirement Description | Priority |
| :--- | :--- | :--- |
| **FR-7.1** | Visualize the Snowflake role hierarchy tree (e.g., ACCOUNTADMIN down to reader roles). | P0 |
| **FR-7.2** | Access Explorer: select a table/view and view a list of all roles/users that can read/write it. | P0 |
| **FR-7.3** | Select a user/role and view all data assets they are authorized to access. | P0 |

---

## 5. Non-Functional Requirements

### Security & Compliance
*   **Local Credential Isolation:** No credentials or database schema metadata are ever sent to an external server.
*   **Encryption at Rest:** Credentials block in database must be encrypted with a master key set in environment variables.

### Performance & Scalability
*   **Inference Query Time:** Blast radius and traversal APIs must resolve in `< 150ms` for graphs up to 50,000 nodes.
*   **Search Latency:** Fuzzy text search autocomplete queries must resolve in `< 50ms`.
*   **Client Render Limit:** The lineage canvas must render up to 500 nodes concurrently without framerate degradation.

### Reliability & Logging
*   **Connector Resiliency:** Sync pipeline must catch network timeouts, retry up to 3 times with exponential backoff, and log specific failure reasons to an audit log.

---

## 6. Main User Flows

```text
1. INGESTION SETUP
User logs in ➔ Goes to "Settings" ➔ Enters Snowflake credentials ➔ Clicks "Test Connection" 
➔ Clicks "Run Ingest" ➔ Sync runs and parses view SQLs ➔ Status turns to "Success"

2. IMPACT AUDIT IN CODE REVIEWS (CI/CD)
GitHub Action triggers PR ➔ Pulls schema change ➔ Calls ImpactGraph /api/v1/impact/blast-radius 
➔ PR comment posted: "⚠️ Renaming total_price has a Blast Radius Score of 45. 8 downstream views affected."

3. SECURITY REVIEW
Auditor searches "USER_EMAILS" table ➔ Clicks "Access Explorer" ➔ Visualizes the inherited role tree 
➔ Identifies that 'MARKETING_INTERN' has inherited read access via a parent role.
```

---

## 7. MVP Acceptance Criteria (Definition of Done)
1.  **Ingestion:** Successfully logs into a target Snowflake instance, parses view definitions, and builds a dependency schema.
2.  **Interactive Lineage:** Can load column lineage showing columns mapping to views and highlights downstream nodes in the web UI.
3.  **Blast Radius Calculation:** Correctly traverses dependency chains to count all downstream nodes.
4.  **CLI/API Integration:** Exposes working REST endpoints returning a JSON payload of downstream dependencies for any given table identifier.
5.  **Self-Hosted Packaging:** The entire platform boots up and connects using local docker compose files with zero manual server configuration.
