# ImpactGraph: Coding Standards

This document establishes the technical rules and patterns for writing code in the ImpactGraph repository. Downstream AI coding agents must comply with these guidelines to ensure consistency, legibility, and maintainability across the entire project.

---

## 1. Directory Structure

The project code is divided into two primary root directories: `/backend` and `/frontend`.

### Backend Directory Layout (Python / FastAPI)
```text
backend/
├── app/
│   ├── api/             # FastAPI route definitions and HTTP validation
│   │   ├── v1/          # API version namespaces
│   │   └── deps.py      # Dependency injection providers (DB, Services)
│   ├── core/            # Global configuration, cryptography, security, and logger setup
│   ├── db/              # SQLAlchemy model definitions and database migration scripts
│   ├── domain/          # Plain Python object entities, interfaces, and algorithms (no ORMs/frameworks)
│   ├── services/        # Application services orchestrating business logic workflows
│   ├── connectors/      # Source platform adapters (Snowflake, Mock connector)
│   │   ├── base.py      # IConnector interface
│   │   └── snowflake/   # Snowflake connector module
│   └── main.py          # API server initialization and routing registration
├── tests/               # Pytest suite
│   ├── unit/            # Business logic and entity unit tests
│   └── integration/     # Database and mocked API integration tests
├── requirements.txt     # Python dependencies
└── Dockerfile           # Backend container build script
```

### Frontend Directory Layout (React / TypeScript / Vite)
```text
frontend/
├── src/
│   ├── components/      # Reusable visual widgets (buttons, modals, tables)
│   ├── pages/           # High-level route views (Dashboard, Lineage Canvas, Explorer)
│   ├── services/        # API communication clients and local state helpers
│   ├── context/         # React context providers (auth, theme)
│   ├── styles/          # Vanilla CSS layout styles (no utility-class frameworks)
│   ├── types/           # TypeScript interface and type declarations
│   ├── main.tsx         # App mount entrypoint
│   └── App.tsx          # High-level routing structure
├── package.json         # JS/TS dependencies
├── vite.config.ts       # Vite packaging configuration
└── Dockerfile           # Frontend container build script
```

---

## 2. Naming Conventions

### Backend (Python - PEP 8)
*   **Modules & Packages:** lowercase, snake_case (`metadata_engine.py`, `lineage.py`).
*   **Classes:** PascalCase (`MetadataRepository`, `SnowflakeConnector`).
*   **Functions & Methods:** lowercase, snake_case (`fetch_schema()`, `calculate_blast_radius()`).
*   **Variables:** lowercase, snake_case (`table_id`, `is_active`).
*   **Constants:** UPPERCASE, snake_case (`AES_KEY_SIZE`, `MAX_RETRIES`).
*   **Interfaces:** Prefix with `I` (`IConnector`, `IMetadataStore`).

### Frontend (TypeScript / CSS)
*   **Component Files:** PascalCase (`LineageGraph.tsx`, `SearchBox.tsx`).
*   **Non-component Files:** camelCase or kebab-case (`apiClient.ts`, `local-storage.ts`).
*   **Variables & Functions:** camelCase (`isLoading`, `handleSubmit()`).
*   **TypeScript Interfaces/Types:** PascalCase (`TableNode`, `ConnectorConfig`).
*   **CSS Classnames:** lowercase, kebab-case (`.metric-card`, `.active-tab`).

---

## 3. Error Handling

### Backend Rules
1.  **Never Catch Bare Exceptions:** Avoid `except:` block. Always catch specific exceptions (e.g., `except snowflake.connector.errors.DatabaseError:`).
2.  **No Secret Exposure:** Never include user credentials or raw SQL query parameters in error strings.
3.  **Traceability:** Raise explicit custom domain errors in services (e.g., `ConnectionFailedError`) and map them to HTTP status codes at the API layer.
4.  **Example:**
    ```python
    # Good Pattern
    try:
        connection = self.snowflake_client.connect()
    except DatabaseError as e:
        logger.error(f"Database connection failed: {e.errno}", exc_info=True)
        raise ConnectionFailedError("Unable to establish connection to target Snowflake account.")
    ```

### Frontend Rules
1.  **Global Boundaries:** Wrap high-level pages (like the Lineage canvas) in React Error Boundaries to catch crashes gracefully.
2.  **API Call Isolation:** Always catch API promise rejections and display a clean toast or alert widget rather than letting the error fail silently.

---

## 4. Logging Standards

*   **Format:** Backend must write structured JSON logs in production environments to support log analytics.
*   **Context:** Include context tags where available (`request_id`, `account_id`, `job_id`).
*   **Secret Masking:** Automatically redact keys named `password`, `token`, `secret`, `passphrase`, or `key` using helper filters before writing to output streams.
*   **Levels:**
    *   `DEBUG`: Low-level database transaction steps, parsed AST info.
    *   `INFO`: Sync startup/completion, API endpoint access logs.
    *   `WARN`: Non-fatal API validation errors, connector timeouts (retries).
    *   `ERROR`: Connection dropouts, unhandled exceptions, sync pipeline aborts.

---

## 5. Testing Requirements

*   **Framework:** Use `pytest` for backend and `Vitest` with React Testing Library for frontend.
*   **Coverage Target:** Keep test coverage of business logic services (`/services`) and utilities at `> 80%`.
*   **Isolation:** Database tests must run on an isolated PostgreSQL/SQLite test database instance that resets schemas before every test run.
*   **Connector Mocking:** Live connectors must use mock mocks (e.g., mock the Snowflake connection object) to verify extraction logic without making outbound network requests.

---

## 6. API Conventions

*   **Design Pattern:** RESTful HTTP exposing JSON structures.
*   **API Prefix:** `/api/v1/`
*   **Resources:** Plural nouns (`/api/v1/tables`, `/api/v1/users`).
*   **HTTP Methods:**
    *   `GET`: Retrieve data (no side effects).
    *   `POST`: Create a new resource or trigger an action (e.g., `/api/v1/jobs/sync`).
    *   `PUT`/`PATCH`: Update an existing resource.
    *   `DELETE`: Remove a resource.
*   **Payload Models:** All input/output models must inherit from Pydantic `BaseModel` on the backend, enforcing strict data validation.
