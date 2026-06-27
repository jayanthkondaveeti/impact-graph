# Project Roadmap: ImpactGraph

This document defines the release plan and future capabilities roadmap for the ImpactGraph platform.

---

## Roadmap Overview

```text
  MVP (Current)          v1.1 (Connectors)       v1.2 (CI/CD & Alert)    v2.0 (Live Parsing)     Enterprise
┌──────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────────┐
│ - Snowflake Sync     │ │ - dbt & Tableau     │ │ - GitHub PR Bot     │ │ - Query Log Parser  │ │ - SAML/OIDC SSO      │
│ - Dependency Graph   │ │ - Search Tags       │ │ - Slack Alerts      │ │ - Column Data Flow  │ │ - Multi-Warehouse    │
│ - Blast Radius API   │ │ - Schema Diffing    │ │ - Lineage REST CLI  │ │ - Quality Overlay   │ │ - Auto-Refactoring   │
└──────────────────────┘ └─────────────────────┘ └─────────────────────┘ └─────────────────────┘ └──────────────────────┘
```

---

## 1. MVP: Core Foundation & Snowflake Lineage (Current Scope)
The primary objective of the MVP is to provide solid structural visibility and change-impact analysis for organizations running on Snowflake.

*   **Snowflake Metadata Connector:** Secure connection using password or keypair authentication. Automatic schema, table, view, column, and RBAC extraction.
*   **SQL View Parser:** Parse `CREATE VIEW` SQL syntax to build column-to-column and table-to-table lineage.
*   **Search Engine:** Simple fuzzy search to locate databases, tables, and columns by name or description.
*   **Lineage Visualizer:** Web interface to render table/column lineage and trace upstream/downstream dependencies.
*   **Blast Radius API:** Algorithmic calculation of downstream impacts. Exposes REST API endpoints for automation.
*   **Operational Risk Engine:** Alerts for "dead views" (views querying non-existent tables) and schemas containing excessive dependencies.
*   **Deployment:** Single command launch via `docker-compose`.

---

## 2. v1.1: Connectors Expansion & Semantic Mapping (Q3 2026)
Expanding boundaries beyond the database warehouse to include data transformation layers and BI dashboards.

*   **dbt Core & Cloud Connector:** Parse dbt project manifest files (`manifest.json`) to pull semantic relationships, column descriptions, and owner tags.
*   **Tableau Connector:** Connect to Tableau metadata API to map database tables and views to specific workbooks, sheets, and dashboards.
*   **Metadata Drift Alerting:** Track database schema history to detect and log modified or deleted columns over time.
*   **Global Tagging & Curation:** Tag critical datasets (e.g., `#PII`, `#FINANCE`, `#GDPR`) in the UI and have tags propagate downstream along lineage paths automatically.

---

## 3. v1.2: Shift-Left CI/CD & Operations (Q4 2026)
Integrating dependency analysis directly into developer workflows to prevent breaking changes from reaching production.

*   **GitHub/GitLab PR Action Bot:** Run ImpactGraph during PR checks. If a developer alters a table, the bot comments on the PR detailing the blast radius and listing affected dashboards.
*   **Lineage CLI:** A developer-friendly command-line interface to query lineage and test refactoring safety locally:
    `impactgraph diff --table CUSTOMERS --column ssn`
*   **Slack/Teams Notifications:** Send automated alerts when schema drift is detected or sync jobs fail.

---

## 4. v2.0: Dynamic Query Logging & Data Quality (H1 2027)
Moving from static schema parsing to dynamic SQL analysis.

*   **Snowflake Query History Parser:** Ingest query logs from Snowflake's `QUERY_HISTORY` views. Parse ad-hoc queries (SELECT, INSERT, MERGE) to build dynamic lineage for staging tables, temporary schemas, and analytical scripts.
*   **Data Quality Lineage Overlay:** Integrate with tools like Great Expectations or Soda. Render data freshness and validation alerts directly on the lineage nodes in the graph canvas.
*   **Column-Level Data Flow Analysis:** Trace how values flow and transform between columns (e.g., column `C` is formed by joining `A` and `B` with a specific multiplier).

---

## 5. Enterprise Capabilities & Automation (H2 2027)
Security, scaling, and automation features required by large enterprises.

*   **SAML/OIDC SSO Integration:** Single Sign-On configuration via Okta, Azure AD, or Ping Identity.
*   **Role-Based Metadata Access Control:** Restrict visibility of specific databases or schemas in the catalog based on user logins.
*   **Multi-DWH support:** Query and link lineage across multiple warehouses (e.g., Snowflake account A joining data with BigQuery dataset B).
*   **AI Auto-Refactoring Agent:** Autonomous agents that write and submit pull requests to refactor downstream dbt code when upstream schemas are changed.
