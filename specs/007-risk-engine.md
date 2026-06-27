# Specification: 007 - Risk Engine

## Overview
This specification details the Operational Risk Engine of ImpactGraph. The engine audits metadata to detect "Dead Objects" (broken views referencing deleted assets), identifies missing ownership, calculates composite object risk scores, and generates optimization recommendations.

---

## Problem Statement
Over time, database schemas accumulate technical debt: views become broken when underlying tables are altered or dropped, tables are left without designated owners, and redundant staging schemas are forgotten. Teams need an automated risk engine that scans database structures, highlights vulnerabilities, and provides prioritized cleanup recommendations.

---

## Goals
*   Detect "Dead Views" (views referencing tables or columns that have been deleted).
*   Identify unowned or unmaintained tables and schemas.
*   Calculate a composite "Operational Risk Score" for every database asset.
*   Formulate actionable cleanup recommendations (e.g., *"Drop Dead View X"*, *"Assign Owner to Table Y"*).
*   Compute an aggregated "Schema Health Score" (0-100) for high-level governance reporting.

---

## User Stories
1.  **As a Data Platform Engineer**, I want a list of all broken Snowflake views so I can delete them and clean up the database catalog.
2.  **As a Data Governance Lead**, I want to identify tables that contain PII data but have no assigned owner.
3.  **As a Chief Data Officer**, I want to see an overall health index score for each database schema to track our technical debt reduction progress.

---

## Functional Requirements
*   **FR-1:** Dead View Detection: Analyze view dependency edges. If any upstream table/view has `is_deleted = TRUE`, flag the downstream view as a `Dead Object`.
*   **FR-2:** Ownership Auditing: Flag any table or schema where the `owner` metadata field is NULL, empty, or set to system defaults (e.g., `INFORMATION_SCHEMA`).
*   **FR-3:** Asset Risk Scoring: Calculate a composite risk score (0 to 100) for every table/view:
    $$\text{Asset Risk Score} = (\text{Blast Radius Score} \times 0.4) + (\text{Is Dead Object} \times 40) + (\text{Missing Owner} \times 20)$$
*   **FR-4:** Recommendations Generator: Periodically compile a list of prioritized recommendations:
    *   *High Priority:* Dead Views referencing active data pipelines.
    *   *Medium Priority:* High-risk tables missing owners.
    *   *Low Priority:* Schemas with high complexity (dependency count > 50).
*   **FR-5:** Schema Health Index: Calculate an aggregate score for each schema based on the ratio of active vs dead/at-risk assets:
    $$\text{Health Index} = 100 \times \left(1 - \frac{\text{Total Dead Views} + 0.5 \times \text{Total Unowned Assets}}{\text{Total Assets in Schema}}\right)$$

---

## UI Requirements
*   **Risk Dashboard Control Panel:**
    *   **Health Cards:** Summary scores for Database Health, Total Broken Views, and Unowned Tables.
    *   **Prioritized Recommendations Feed:** List of cleanup recommendations, with action buttons to "View Lineage" or "Go to Object Page".
    *   **Risk Heatmap Grid:** A modular layout representing schemas, colored from Green (Healthy) to Red (High Technical Debt).

---

## Backend Requirements
*   **Domain Service:** `RiskEngineService` containing calculation formulas.
*   **Execution Trigger:** Recalculate risk states immediately after metadata sync completions.

---

## Database Changes
We must store calculated risk scores in a new table:

```sql
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL UNIQUE REFERENCES tables(id),
    composite_score REAL DEFAULT 0.0,
    is_dead BOOLEAN DEFAULT FALSE,
    missing_owner BOOLEAN DEFAULT FALSE,
    recommendations_json TEXT, -- JSON array of generated warnings
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

### 1. Risk Recommendations List
*   `GET /api/v1/risk/recommendations`
    *   **Parameters:**
        *   `priority` (Optional: 'HIGH', 'MEDIUM', 'LOW')
        *   `limit` (default 50)
    *   **Response (200 OK):**
        ```json
        [
          {
            "id": "uuid",
            "title": "Broken View Detected",
            "description": "View CUSTOMER_LOGINS queries deleted table RAW_LOGINS.",
            "priority": "HIGH",
            "target_table_id": "uuid",
            "created_at": "timestamp"
          }
        ]
        ```

### 2. Schema Health Indices
*   `GET /api/v1/risk/schemas/health`
    *   **Response (200 OK):**
        ```json
        [
          {
            "schema_id": "uuid",
            "schema_name": "PUBLIC",
            "database_name": "PROD_DB",
            "health_score": 92.5,
            "total_assets": 140,
            "dead_assets_count": 3
          }
        ]
        ```

---

## Acceptance Criteria
1.  Deleting a table in a mock sync run instantly flags all views directly query-referencing it as `is_dead = TRUE` and creates a high-priority recommendation.
2.  Risk scoring equations match specifications and correctly output ratings within the `0.0` to `100.0` bounds.
3.  Recommendations list updates automatically on sync completion and is cleared if the underlying issue is resolved (e.g., if a table is restored or recreated).
4.  Standard unit tests cover the calculations of both Asset Risk and Schema Health indexes.

---

## Out of Scope
*   Executing cleanup SQL scripts on Snowflake (ImpactGraph remains strictly read-only).
*   Analyzing code repositories (e.g. Git folders) to trace code files queries.

---

## Future Enhancements
*   Alerting via Slack/Teams when a new dead view is detected.
*   Assigning custom weights to risk scoring variables.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 003 - Metadata Engine (loaded schemas and deleted states).
*   Spec 006 - Impact Analysis (blast radius inputs).
