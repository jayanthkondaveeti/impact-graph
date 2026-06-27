# Specification: 001 - Project Foundation

## Overview
This specification details the foundational architecture of the ImpactGraph repository. It establishes the workspace setup, Docker multi-container orchestrations, database migration pipeline, global environment configuration, and local authentication controls.

---

## Problem Statement
Developing a complex, multi-container system requires a reliable, standard local execution environment. To ensure developers and autonomous AI agents write compatible modules, we must specify the exact repository layout, Docker configuration, database migration patterns, and credentials management mechanisms before implementing functional features.

---

## Goals
*   Provide a single-command local deployment workflow using `docker-compose`.
*   Establish an encrypted credentials storage system in PostgreSQL using AES-256.
*   Secure the backend APIs using JSON Web Token (JWT) stateless sessions.
*   Configure the backend schema migration engine with Alembic.
*   Enforce TypeScript and strict type-safety boundaries in the React frontend.

---

## User Stories
1.  **As a Data Engineer**, I want to download the repository and run `docker-compose up` to boot the frontend, backend, and PostgreSQL database without setting up local database drivers.
2.  **As a Platform Admin**, I want to input my Snowflake credentials securely in the UI settings panel and know they are encrypted before being written to disk.
3.  **As an API Consumer**, I want to authenticate via an endpoint and receive a secure token to query the blast-radius metadata programmatically.

---

## Functional Requirements
*   **FR-1:** Bootstrapping: Docker compose file must orchestrate three services: `backend`, `frontend`, and `db` (PostgreSQL 15).
*   **FR-2:** Backend Boot: FastAPI must auto-run pending database migrations (Alembic) on container startup.
*   **FR-3:** Encryption: Credentials stored in `databases.connection_config` must be encrypted using `cryptography.hazmat.primitives.ciphers` with a 256-bit key provided in the `IMPACTGRAPH_SECRET_KEY` environment variable.
*   **FR-4:** Authentication: Single-user local admin authentication. Passwords must be hashed using `bcrypt` and stored in the `users` database table.
*   **FR-5:** Token Auth: API access is restricted using a `Bearer` token (JWT containing user ID, signed with HMAC-SHA256, expiring in 24 hours).

---

## UI Requirements
*   **Login Canvas:** A clean, centered, card-based login page. Shows validation feedback for invalid passwords.
*   **Portal Frame:** Sidebar layout containing a logo, navigation links (Dashboard, Explorer, Audits, Settings), and a log-out button.
*   **Settings Form:** Form fields to configure database credentials (Host, Account, Username, Password, Warehouse, Database). Clicks "Test Connection" and "Save".

---

## Backend Requirements
*   **Framework:** FastAPI running on Python 3.9+ with Uvicorn.
*   **ORM Layer:** SQLAlchemy 2.0+ with PostgreSQL driver `psycopg2-binary`.
*   **Migration Tool:** Alembic configured in the `/backend` root directory.
*   **Security Libraries:** `jose` (for JWT operations), `passlib[bcrypt]` (for password hashes), and `cryptography` (for AES credentials encryption).

---

## Database Changes
The baseline database schema requires two initial tables:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL, -- e.g., 'snowflake'
    connection_config TEXT NOT NULL, -- AES-256 encrypted JSON payload
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

### 1. Authentication
*   `POST /api/v1/auth/login`
    *   **Description:** Authenticate user credentials.
    *   **Request Body:** `{"username": "admin", "password": "secure_password"}`
    *   **Response (200 OK):** `{"access_token": "jwt_token_string", "token_type": "bearer"}`

### 2. Configuration Management
*   `GET /api/v1/config/connection`
    *   **Description:** Get configured connection names (passwords masked).
    *   **Response (200 OK):** `[{"id": "uuid", "name": "prod_snowflake", "platform": "snowflake"}]`
*   `POST /api/v1/config/connection`
    *   **Description:** Save new encrypted database credentials.
    *   **Request Body:** `{"name": "prod_snowflake", "platform": "snowflake", "config": {...}}`
    *   **Response (201 Created):** `{"id": "uuid", "name": "prod_snowflake"}`

---

## Acceptance Criteria
1.  Running `docker-compose up --build` launches the application and displays the React login page at `http://localhost`.
2.  Logging in with valid admin credentials successfully loads the Dashboard workspace and returns a signed JWT.
3.  Saving a Snowflake connector config stores an encrypted payload in the `databases` table (verifiable by inspecting the DB directly to confirm credentials are obfuscated).
4.  Standard unit tests pass with `pytest`.

---

## Out of Scope
*   Multi-user self-registration (user is pre-seeded in the database migration script).
*   Password recovery/reset emails.
*   OAuth2, SAML, or LDAP authentication providers.

---

## Future Enhancements
*   Adding Multi-Factor Authentication (MFA).
*   Role-Based access restrictions on individual metadata pages within ImpactGraph.

---

## Dependencies
*   Python standard environment variables.
*   Local Docker daemon installation.
