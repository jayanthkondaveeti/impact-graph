# ImpactGraph 🛡️

**ImpactGraph** is an open-source **Data Impact Analysis Platform** designed for data platform engineers to trace column-level lineages, compute downstream blast-radius risks of schema migrations, audit role privilege access paths, and reduce warehouse costs by identifying dead assets.

---

## 🚀 Core Features

*   **Column-Level Lineage Tracing:** Decodes complex views and CTEs to trace columns from raw source tables down to final reporting structures.
*   **Downstream Blast-Radius Analysis:** Instantly calculates risk scores representing the downstream assets (tables, columns, views) that will break if a field is modified.
*   **Nested RBAC Privilege Mapping:** Crawls Snowflake role hierarchies and object grants to trace exactly why a specific role has privileges on a database target.
*   **Cost-Efficient Metadata Syncing:** Reads catalog schemas and view definitions without accessing row data values, consuming < 0.1 Snowflake credits per day.
*   **CI/CD Pipeline Guard (Roadmap):** Plugs directly into GitHub Pull Requests to alert developers if their SQL modifications will break downstream tables.

---

## 💡 Key Use Cases

### 1. Schema Migration Pre-Checks (Preventing Production Outages)
*   **The Scenario:** A data engineer needs to rename the column `customer_id` to `customer_uuid` in a central database table.
*   **The ImpactGraph Solution:** Traces the column lineage downstream, showing that the column is consumed by 3 SQL views and an executive Looker dashboard. It calculates a high blast-radius score, prompting the team to update downstream views *before* deploying the schema change.

### 2. Access Auditing & Compliance (GDPR & SOC 2)
*   **The Scenario:** A compliance auditor asks: *"Why does the marketing analyst role have read access to the sensitive customer billing table?"*
*   **The ImpactGraph Solution:** Traces the role inheritance path, showing that the `MARKETING_ANALYST` role inherits permissions from the `DATA_ENGINEER` role which has SELECT privilege on the billing table. The administrator can prune the incorrect inheritance path in seconds.

### 3. Orphaned Asset Cleanup (Reducing Cloud Warehouse Spend)
*   **The Scenario:** The database contains hundreds of legacy views, and database storage/compute costs are rising.
*   **The ImpactGraph Solution:** The health risk engine flags "dead views" (views referencing underlying tables that were deleted weeks ago) and "unowned assets" that can be safely purged to reduce warehouse clutter and compute load.

### 4. Root-Cause Analysis (Debugging Data Quality Incidents)
*   **The Scenario:** A business analyst reports that the `total_revenue` column in a dashboard is skewed.
*   **The ImpactGraph Solution:** Lineage traversal traces the column's lineage back through 4 intermediate views to the exact source tables and SQL equations, allowing engineers to isolate where the calculation error was introduced.

---

## 🛠️ Technology Stack

*   **Backend Application:** Python 3.9, FastAPI (Asynchronous REST API), Pydantic (data validations).
*   **Database & Migration:** PostgreSQL 15, SQLAlchemy ORM (13 schema models defined), Alembic migration engine.
*   **Graph Traversal & Analysis:** `NetworkX` (in-memory graph cache), `sqlglot` (SQL view AST query parser).
*   **Credentials Cryptography:** AES-256-CBC envelope encryption using local key variables.
*   **Frontend Client:** React 18 (TypeScript), Vite, React Flow (interactive node-edge canvas diagrams), Lucide.
*   **DevOps & Reverse Proxy:** Docker Compose, Nginx (routing static builds and proxying `/api/*` upstream).

---

## 📁 Repository Structure

```text
impactgraph/
├── docker-compose.yml       # Coordinates Database, Backend, and Frontend containers
├── .env                     # Local environment keys and configuration profiles
├── .gitignore               # Keeps compiled binaries and secret parameters out of Git
├── README.md                # Project documentation landing page
├── LICENSE                  # Open-source license agreement
├── backend/
│   ├── app/                 # FastAPI routes, database models, session logic, and encryptors
│   ├── migrations/          # Alembic DDL migration scripts (seeds admin account)
│   ├── alembic.ini          # Migration setup
│   ├── start.sh             # Wait-for-DB wait checks and boot script
│   └── Dockerfile           # Python compiler container build
└── frontend/
    ├── src/                 # React views (Dashboard, Settings, Login, and API clients)
    ├── nginx.conf           # Nginx reverse proxy routing profiles
    ├── vite.config.ts       # Vite compiler config
    └── Dockerfile           # Multi-stage Node package build
```

---

## ⚡ Quick Start

### 1. Prerequisites
Make sure you have **Docker Desktop** running on your machine.

### 2. Launch the Stack
Initialize the database, execute migrations, compile React assets, and launch the services:
```bash
docker-compose up -d --build
```

This starts the following containers:
*   **Frontend Client:** Accessible at [http://localhost](http://localhost) (mapped to port 80).
*   **FastAPI Backend Server:** Accessible at [http://localhost:8000](http://localhost:8000) (interactive OpenAPI docs at `http://localhost:8000/docs`).
*   **Postgres Catalog Database:** Listening on port `5432`.

### 3. Log In
Open the frontend and sign in using the seeded default administrator account:
*   **Username:** `admin`
*   **Password:** `password123`

### 4. Setup Snowflake Sync
1.  Navigate to **Settings** in the portal sidebar.
2.  Input your Snowflake Trial Account ID, Username, Password, default Warehouse (`DEVELOPER_WH`), and Database (`DEMO_DB`).
3.  Click **Save Configuration**.
4.  Return to the **Dashboard** and click **Trigger Database Sync**. Watch the metrics populate live!
