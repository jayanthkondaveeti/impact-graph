# Specification: 009 - Dashboard

## Overview
This specification details the central Landing Page and Dashboard UI workspace for ImpactGraph. The dashboard aggregates global metrics, lists operational warnings, tracks recent schema activity, and displays synchronization connector statuses.

---

## Problem Statement
Users need a central homepage to monitor the status of their data catalog. Without an aggregate dashboard, data leads cannot quickly gauge the technical debt of their schemas, monitor active ingestion jobs, or track recent schema modifications.

---

## Goals
*   Provide a landing workspace summarizing warehouse health indices.
*   Expose aggregated metrics: Total Tables/Views, Unowned Assets, and Dead Views.
*   List a "Recent Activity Feed" displaying schema drift events.
*   Display a "Sync Pipeline Status" card monitoring active and historical ingestion runs.
*   Integrate a prominent search box to serve as the homepage entry point.

---

## User Stories
1.  **As a Data Director**, I want to open the homepage and instantly see that our overall Data Warehouse Health Score is 94.2%.
2.  **As a Data Engineer**, I want to check the dashboard's recent activity feed to verify which columns were added or renamed during yesterday's dbt deploy.
3.  **As a Platform Admin**, I want to see if the scheduled Snowflake metadata sync job completed successfully this morning.

---

## Functional Requirements
*   **FR-1:** Metadata Aggregations: Calculate warehouse metrics:
    *   `total_databases`, `total_schemas`, `total_tables`, `total_views`
    *   `total_dead_views`, `total_unowned_tables`
*   **FR-2:** Global Health Index Calculation: Compute the average health score across all active schemas.
*   **FR-3:** Ingestion Status Monitoring: Query the `sync_jobs` table to extract:
    *   Current job status (RUNNING, SUCCESS, FAILED).
    *   Last success execution timestamp.
    *   Total records ingested.
*   **FR-4:** Recent Activity Feed: Fetch and display the 10 most recent records from the `schema_history` table, sorted by detection date.

---

## UI Requirements
*   **Dashboard Workspace Grid:**
    *   **Hero Cards:** Four glassmorphic stats cards (Health Score, Total Tables, Broken Views, Unowned Assets).
    *   **Search Section:** A large centered search input with autocomplete suggestions.
    *   **Activity Feed Panel:** List of recent schema events with clean icon labels (e.g. green plus for column added, red minus for column deleted).
    *   **Pipeline Status Card:** Status card with a pulsating dot showing sync progress, elapsed execution time, and error logs if failed.

---

## Backend Requirements
*   **Aggregation Optimizations:** Cache database counts and health averages using a temporary redis cache or in-memory python dictionary to prevent running heavy SQL queries on every page load.

---

## Database Changes
No new tables required. This specification compiles data from `tables`, `columns`, `sync_jobs`, `schema_history`, and `risk_scores` tables.

---

## API Endpoints

### 1. Dashboard Statistics
*   `GET /api/v1/dashboard/stats`
    *   **Response (200 OK):**
        ```json
        {
          "warehouse_health_score": 94.2,
          "counts": {
            "databases": 2,
            "schemas": 12,
            "tables": 240,
            "views": 80
          },
          "alerts": {
            "dead_views_count": 4,
            "unowned_assets_count": 18
          },
          "last_sync": {
            "status": "SUCCESS",
            "completed_at": "2026-06-27T02:00:12Z",
            "duration_seconds": 45
          }
        }
        ```

### 2. Recent Activity Feed
*   `GET /api/v1/dashboard/activity`
    *   **Parameters:** `limit` (default 10)
    *   **Response (200 OK):**
        ```json
        [
          {
            "id": "uuid",
            "table_name": "FACT_SALES",
            "change_type": "COLUMN_ADDED",
            "target": "DISCOUNT_PERCENT",
            "detected_at": "2026-06-27T02:00:08Z"
          }
        ]
        ```

---

## Acceptance Criteria
1.  Accessing the landing page loads all summary metric cards in `< 1.5 seconds`.
2.  Triggering a metadata sync updates the pipeline status card in real-time (polling or web-sockets).
3.  The Health Score card accurately mirrors changes to the underlying `risk_scores` table data.
4.  Standard unit tests mock the aggregation service to verify math calculations.

---

## Out of Scope
*   User-customizable dashboard widgets (fixed layout for MVP).
*   Exporting dashboard reports in PDF or XLSX format.

---

## Future Enhancements
*   Adding WebSockets to push sync job updates to the UI in real-time without polling.
*   Data usage query popularity tracking charts on the homepage.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 002 - Snowflake Connector (sync status).
*   Spec 003 - Metadata Engine (activity feed).
*   Spec 007 - Risk Engine (health indexes).
