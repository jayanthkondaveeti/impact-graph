# Brainstorm: Connector & Integration Ideas

This document outlines future connector modules that can extend ImpactGraph's lineage coverage beyond Snowflake.

---

## 1. Google BigQuery Connector
*   **Mechanism:** Extract metadata from BigQuery's `INFORMATION_SCHEMA` tables.
*   **Queries:** Query `INFORMATION_SCHEMA.TABLES` and `INFORMATION_SCHEMA.COLUMN_FIELD_PATHS` (handling nested records/STRUCTs).
*   **Lineage:** Retrieve SQL queries from Google Cloud Logging audit logs to build dynamic lineage.

---

## 2. dbt (Data Build Tool) Manifest Ingestor
*   **Mechanism:** Ingest the dbt compiled output file `manifest.json`.
*   **Mapping:** 
    *   dbt nodes (models, seeds, sources) map to Table nodes.
    *   `depends_on.nodes` lists map directly to dependency edges.
    *   dbt description and owner configs map to metadata attributes.
*   **Why it's important:** dbt provides clean semantic mappings that bypass the need to parse SQL code manually.

---

## 3. Apache Airflow DAG Tracker
*   **Mechanism:** Parse Python DAG files using AST analysis or listen to OpenLineage events.
*   **Extraction:** Find tasks executing SQL queries (e.g. `SnowflakeOperator`) and map the task execution edge in our graph as a step between the source and destination tables.

---

## 4. Ingestion Drivers (Fivetran & Airbyte)
*   **Mechanism:** Connect to the Fivetran/Airbyte REST API.
*   **Extraction:** Map replication tasks. If Fivetran replicates Salesforce `Account` tables into Snowflake `STG_SF_ACCOUNTS`, write an ingestion lineage link connecting the Salesforce CRM source system to the warehouse table.

---

## 5. BI Dashboards (Tableau & Looker)
*   **Mechanism:** Query Tableau Metadata GraphQL API or Looker LookML definitions.
*   **Extraction:** Map sheets and dashboards. Connect database views to specific reporting assets, completing the "source-to-report" lifecycle.
