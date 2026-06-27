# Specification: 004 - Search

## Overview
This specification details the global search engine for ImpactGraph. The search engine indexes databases, schemas, tables, and columns, providing autocomplete suggestions, fuzzy search matching, result ranking, and facet filtering.

---

## Problem Statement
Finding specific data assets in large-scale warehouses with thousands of tables is slow and frustrating without structured search. Users need a search interface that can scan table and column attributes, handle minor typos (fuzzy matching), provide instant autocomplete, and rank results so that the most relevant objects appear first.

---

## Goals
*   Implement global fuzzy search across database, schema, table, and column names.
*   Deliver instant autocomplete suggestions as the user types (latency < 50ms).
*   Rank results based on match location (e.g., exact table name matches rank higher than column description matches).
*   Provide search filters (facets) to narrow results by database, schema, object type, and owner.
*   Index database text fields to support performant query execution without external servers.

---

## User Stories
1.  **As a Analytics Engineer**, I want to type "trans" in the search box and see `FACT_TRANSACTIONS` appear at the top of the autocomplete dropdown.
2.  **As a Compliance Officer**, I want to search for the word "email", filter results to show only "Columns", and see which tables contain email fields.
3.  **As a Developer**, I want the search engine to return relevant results even if I make a small typo (e.g., searching for "custmer" instead of "customer").

---

## Functional Requirements
*   **FR-1:** Fuzzy Search: Match user queries against metadata records using PostgreSQL Trigram similarity matching.
*   **FR-2:** Autocomplete: Provide a lightweight endpoint returning up to 5 matching suggestions based on prefix matching.
*   **FR-3:** Faceted Filters: Support filtering search results by:
    *   `database_id` / `schema_id`
    *   `type` (Table vs View)
    *   `owner`
    *   `column_only` (Boolean flag)
*   **FR-4:** Relevance Ranking: Rank matching records using the following weight heuristics:
    1.  Exact match on Table/View name (Weight: 1.0)
    2.  Fuzzy/Trigram match on Table/View name (Weight: 0.8)
    3.  Exact match on Column name (Weight: 0.6)
    4.  Match inside table/column descriptions (Weight: 0.3)
*   **FR-5:** Pagination: Support standard offset/limit pagination parameters on the main search endpoint.

---

## UI Requirements
*   **Search Box Dropdown:** A clean, floating input box. Typing triggers an autocomplete list with icons matching the asset type.
*   **Search Results Explorer:**
    *   Left column: Filter sidebar (collapsible checkboxes for Database, Schema, Type, Owner).
    *   Right column: List of matching cards. Each card displays:
        *   Asset Name (highlighting matching letters).
        *   Fully qualified path (`prod_db ➔ sales ➔ tables`).
        *   Description snippet.
        *   Primary Owner and row count.
        *   List of matching columns (if search query matched column names).

---

## Backend Requirements
*   **Text Indexing:** PostgreSQL GIN (Generalized Inverted Index) using the `pg_trgm` extension.
*   **ORM Queries:** SQLAlchemy SELECT statements with PostgreSQL-specific operators (`%` for trigram similarity).

---

## Database Changes
We must enable the trigram extension and build GIN indexes to support fast fuzzy matching:

```sql
-- Run in PostgreSQL database migration
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Index table names for trigram search
CREATE INDEX idx_tables_name_trgm ON tables USING gin (name gin_trgm_ops);

-- Index column names for trigram search
CREATE INDEX idx_columns_name_trgm ON columns USING gin (name gin_trgm_ops);
```

---

## API Endpoints

### 1. Global Search
*   `GET /api/v1/search`
    *   **Parameters:**
        *   `q` (Query string, required)
        *   `type` (Optional, 'TABLE' or 'VIEW')
        *   `database_id` (Optional UUID)
        *   `limit` (default 20)
        *   `offset` (default 0)
    *   **Response (200 OK):**
        ```json
        {
          "total_results": 1,
          "results": [
            {
              "id": "uuid",
              "name": "FACT_SALES",
              "type": "TABLE",
              "database_name": "PROD_DB",
              "schema_name": "PUBLIC",
              "score": 0.95,
              "owner": "SALES_OPS",
              "description": "Historical sales transaction records"
            }
          ]
        }
        ```

### 2. Autocomplete Suggestions
*   `GET /api/v1/search/autocomplete`
    *   **Parameters:** `q` (Query string, required)
    *   **Response (200 OK):**
        ```json
        [
          {"id": "uuid", "name": "CUSTOMERS", "type": "TABLE", "path": "PROD_DB.PUBLIC.CUSTOMERS"},
          {"id": "uuid", "name": "CUSTOMER_LOGINS", "type": "VIEW", "path": "PROD_DB.PUBLIC.CUSTOMER_LOGINS"}
        ]
        ```

---

## Acceptance Criteria
1.  Fuzzy search handles minor typos (e.g. typing "salss" returns results containing "sales").
2.  Autocomplete queries return matching suggestions in `< 50ms`.
3.  Clicking a search filter checkbox immediately updates the list of results via AJAX.
4.  Standard SQL indices are applied correctly; query plans for search show index scans instead of full table scans.

---

## Out of Scope
*   Integrating external search engines like ElasticSearch, OpenSearch, or Algolia.
*   Indexed search inside actual database table values (schema metadata only).

---

## Future Enhancements
*   Adding search synonyms support (e.g., mapping "DWH" to "Data Warehouse").
*   Advanced query syntax support (e.g. `owner:Elena type:view orders`).

---

## Dependencies
*   Spec 001 - Project Foundation (database connection).
*   Spec 003 - Metadata Engine (loaded schemas).
