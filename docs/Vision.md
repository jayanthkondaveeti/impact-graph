# ImpactGraph - Strategic Vision

## 1. Executive Summary & Mission

### Mission Statement
To establish the definitive open-source data impact analysis platform that empowers modern engineering teams to seamlessly map, query, govern, and analyze metadata and dependency networks across all data platforms.

### Core Philosophy: Lineage is Operational, Not Visual
Traditional data catalogs focus heavily on rendering complex "lineage graphs"—spaghetti-like visualizations that look impressive but are operationally useless for automated pipelines and day-to-day engineering. 

**ImpactGraph shifts the paradigm from visual discovery to operational analysis.** 

We believe lineage should be treated as a queryable, indexable, and computable graph of dependencies. Instead of asking engineers to stare at a UI to trace a table's origin, ImpactGraph answers programmatic engineering questions via APIs and CLI integrations during CI/CD execution:
*   *Is it safe to drop this column on Snowflake?*
*   *What is the exact list of downstream Tableau dashboards that will break if this dbt model is modified?*
*   *Does this service account have unauthorized cross-database read access?*
*   *What is the blast radius score of this schema change?*

---

## 2. Product Philosophy & Guiding Principles

To build a platform that developers love and security teams trust, ImpactGraph adheres to five core product design principles:

### I. API-First & Query-Driven
Every capability exposed in the UI must be powered by a robust, well-documented REST/GraphQL API. Visual graphs are secondary representations of computable graph queries.

### II. Actionable Insights Over Information Dumping
We do not aim to catalog every single byte of data. We focus on identifying **structural risk**, **unused assets**, **access privilege escalation**, and **lineage gaps**. ImpactGraph provides active recommendations rather than passive observation.

### III. Connector-Plugin Architecture
The core engine is independent of any specific data platform. Platforms (Snowflake, BigQuery, dbt, Tableau) are integrated via modular plugins. Adding a new database connector should be as simple as implementing a Python interface.

### IV. Lightweight & Self-Hostable
ImpactGraph must run efficiently on local machines (via Docker Compose) and scale horizontally inside Kubernetes environments without requiring massive multi-tenant SaaS infrastructure or proprietary graph databases.

### V. Security & Governance by Default
ImpactGraph handles sensitive database credentials and schema metadata. The platform must support fine-grained RBAC, encrypt credentials at rest, support private networking, and store no actual customer transaction data.

---

## 3. Target User Personas

ImpactGraph is designed for three core personas within modern data-driven organizations:

### The Data Platform Engineer (Operator)
*   **Context:** Manages data warehouses (Snowflake, BigQuery), orchestrators (Airflow), and transformation pipelines (dbt).
*   **Needs:** To clean up the warehouse by deleting unused tables, refactoring models safely, and ensuring database access credentials are secure.
*   **Friction:** Fear of breaking critical, unknown downstream dashboards or pipelines when making refactoring changes.

### The Analytics Engineer & Analyst (Consumer)
*   **Context:** Builds reports, semantic models, and BI dashboards (Tableau, Looker).
*   **Needs:** To know where their data comes from, identify why a dashboard is displaying incorrect numbers, and verify ownership of a table.
*   **Friction:** Stale documentation, long debug cycles tracing data back through 15 layers of views, and lack of clarity on data freshness.

### The Data Governance & Compliance Officer (Auditor)
*   **Context:** Audits data privacy (PII tracking), verifies access control (RBAC), and monitors security posture.
*   **Needs:** Comprehensive visibility into which roles and users have access to sensitive columns, tracing data flow to ensure PII does not leak into unauthorized reports.
*   **Friction:** Manual audits, lack of unified access graphs, and inability to trace column-level lineage across database boundaries.

---

## 4. Platform Success Metrics

The success of the ImpactGraph platform will be measured by the following metrics:

*   **Ingestion Performance:** Time taken to parse metadata and build a graph containing 10,000 tables and 100,000 columns (Target: < 2 minutes).
*   **Query Latency:** Blast radius computation response time via API (Target: < 100ms for up to 5 degrees of separation).
*   **Lineage Accuracy:** Precision and recall of column-level dependencies parsed from SQL queries and view definitions (Target: > 98% accuracy).
*   **Refactoring Safety:** Elimination of "broken dashboard" incidents in organizations using ImpactGraph in their CI/CD pipelines.

---

## 5. Future Evolution & Horizon Vision

```text
  Phase 1 (MVP)          Phase 2 (v1.x)         Phase 3 (v2.0)         Phase 4 (Enterprise)
┌──────────────────────┐ ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────────┐
│ - Snowflake Metadata │ │ - dbt & Tableau    │ │ - Real-time Query  │ │ - Autonomous Refactor  │
│ - Dependency Graph   │ │   Connectors       │ │   Parsing (Parser) │ │   Agents (AI Auto-Fix) │
│ - Blast Radius API   │ │ - CI/CD PR Bot     │ │ - Data Quality     │ │ - Federated Multi-     │
│ - Simple Web Portal  │ │ - Basic Alerting   │ │   Lineage Sync     │ │   Cloud Governance     │
└──────────────────────┘ └────────────────────┘ └────────────────────┘ └────────────────────────┘
```

*   **Horizon 1 (MVP):** Standard metadata extraction for Snowflake, providing table/column dependency graphs, basic risk scores, and a search engine.
*   **Horizon 2 (v1.x):** Integration with dbt and Tableau to enable complete end-to-end lineage (from raw source database to BI dashboard) and GitHub Action integrations to warn developers of breaking changes on Pull Requests.
*   **Horizon 3 (v2.0):** Native SQL parser parsing active query histories (e.g., from Snowflake Query History) to dynamically draw lineage for temporary tables and ad-hoc analytical workloads.
*   **Horizon 4 (Enterprise):** Auto-remediation agents that automatically generate dbt pull requests to refactor downstream dependencies when an upstream database table is migrated or deprecated.
