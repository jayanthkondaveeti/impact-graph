# Specification: 006 - Impact Analysis

## Overview
This specification details the Impact Analysis engine for ImpactGraph. The engine calculates the downstream "Blast Radius" score, traverses dependency networks, and compiles change-preview reports when database assets (tables or columns) are altered, deleted, or refactored.

---

## Problem Statement
Altering a table schema or dropping a column frequently causes silent downstream failures in views, dbt models, and reports. Data engineers need a predictive impact analysis service that traverses the dependency network, calculates an operational risk score, and lists all affected assets before any SQL DDL changes are executed.

---

## Goals
*   Calculate a numerical "Blast Radius Score" indicating the severity of modifying a specific object.
*   Identify all downstream database tables, views, and columns that depend on a targeted asset.
*   Provide a "Safe Delete" validation API to verify if an asset has zero downstream dependencies.
*   Expose programmatic endpoints suitable for CI/CD pipeline integration (e.g., GitHub Action pull request checkers).

---

## User Stories
1.  **As a Platform Engineer**, I want to query the blast radius of dropping `COLUMN_X` from the `FACT_ORDERS` table and see a list of the 15 downstream views that will break.
2.  **As an Analytics Engineer**, I want the CI/CD pipeline to automatically block a pull request if the schema migration has a blast radius score exceeding 50.
3.  **As a Data Analyst**, I want to check a "Change Preview" before renaming a column to see which reports I will need to update.

---

## Functional Requirements
*   **FR-1:** Downstream Traversal: Extract the set of all downstream nodes (descendants) in the graph starting from the target table or column.
*   **FR-2:** Blast Radius Calculation: Calculate a numeric score (0 to 100) using the following formula:
    $$\text{Blast Radius} = \text{MIN}\left(100, \sum (\text{Downstream Tables} \times 2.0) + (\text{Downstream Columns} \times 0.5)\right)$$
*   **FR-3:** Safe Delete Check: Provide a boolean indicator returning `TRUE` if downstream dependencies equal `0`, and `FALSE` if any dependent assets exist.
*   **FR-4:** Path Trace Mapping: Include the shortest path traces (relationships) from the target node to each affected downstream asset, helping engineers understand *why* an asset is impacted.
*   **FR-5:** CI/CD Integration Payload: Return a structured JSON summary suitable for markdown parsing in pull request comments.

---

## UI Requirements
*   **Impact Summary Tab:** Located on the object details workspace. Contains:
    *   **Score Badge:** Large numeric indicator colored by severity (Red = High >50, Amber = Medium 20-50, Green = Low <20).
    *   **Downstream Metrics:** Total tables, columns, and views impacted.
    *   **Dependency Tree View:** A collapsible list layout showing downstream objects organized by degree of separation (Direct, 2nd Degree, 3rd Degree).
    *   **Safe Delete Indicator:** A status banner indicating whether the asset can be deleted immediately.

---

## Backend Requirements
*   **Algorithm Library:** `networkx` graph traversal methods:
    *   `networkx.descendants(graph, node)` to find all affected children.
    *   `networkx.shortest_path(graph, source, target)` to extract lineage traces.
*   **Response Payload Model:** FastAPI Pydantic schema returning summary stats, node lists, and trace details.

---

## Database Changes
No new tables required. This specification operates on the `dependencies`, `tables`, and `columns` schemas.

---

## API Endpoints

### 1. Blast Radius Score & Summary
*   `GET /api/v1/impact/blast-radius/{table_id}`
    *   **Response (200 OK):**
        ```json
        {
          "table_id": "uuid",
          "table_name": "FACT_SALES",
          "blast_radius_score": 64.0,
          "is_safe_to_delete": false,
          "summary": {
            "total_tables_affected": 8,
            "total_views_affected": 12,
            "total_columns_affected": 48
          },
          "affected_assets": [
            {
              "id": "uuid",
              "name": "SALES_SUMMARY_VIEW",
              "type": "VIEW",
              "degree_of_separation": 1,
              "owner": "SALES_ANALYST"
            }
          ]
        }
        ```

### 2. Column Change Impact Preview
*   `POST /api/v1/impact/preview`
    *   **Request Body:**
        ```json
        {
          "table_id": "uuid",
          "column_name": "total_price",
          "action": "DROP_COLUMN" -- 'DROP_COLUMN' or 'RENAME_COLUMN'
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
          "action": "DROP_COLUMN",
          "blast_radius_score": 12.5,
          "is_safe_to_delete": false,
          "affected_columns": [
            {
              "column_id": "uuid",
              "column_name": "gross_margin",
              "table_name": "SALES_AGGREGATE_VIEW",
              "path_trace": ["FACT_SALES.total_price", "SALES_AGGREGATE_VIEW.gross_margin"]
            }
          ]
        }
        ```

---

## Acceptance Criteria
1.  Querying a table blast radius accurately crawls the entire downstream DAG branch, returning all indirect view dependencies.
2.  The API resolves traversal and scoring for a graph of 10,000 nodes in under `100ms`.
3.  The calculation of Blast Radius Score matches the formula and caps at exactly `100.0`.
4.  Safe delete checker returns `true` only if no other tables or columns query or reference the target object.

---

## Out of Scope
*   Automated refactoring of downstream view code to fix broken columns.
*   Integrating directly with Tableau APIs in the MVP (limited to database assets).

---

## Future Enhancements
*   Integrating with Slack webhooks to notify table owners when a downstream dependency changes.
*   Simulated migration sandboxes.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 003 - Metadata Engine (lineage schema).
*   Spec 005 - Lineage (graph traversal cache).
