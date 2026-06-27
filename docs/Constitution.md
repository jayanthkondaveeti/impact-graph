# ImpactGraph: Engineering Constitution

This constitution defines the immutable engineering principles that must govern the design, development, and expansion of ImpactGraph. Every developer, architect, and autonomous coding agent must adhere to these rules without exception. Code that violates these tenets will be rejected during code reviews.

---

## The Core Tenets

### 1. API-First Design
*   **The Law:** The user interface (frontend) is merely a client consuming public APIs. There must be no proprietary database access, calculations, or logic hidden in the UI layer.
*   **The Implementation:** Every visualization, lineage query, or config state change must be exposed via standard REST/GraphQL endpoints first. These endpoints must be fully documented using OpenAPI/Swagger before frontend implementation begins.

### 2. Clean Architecture & Separation of Concerns
*   **The Law:** The business domain model must remain pure and independent of database drivers, transport frameworks (HTTP/gRPC), and external vendor APIs.
*   **The Implementation:** 
    *   **Domain Layer:** Holds data models (Table, Column, Grant) and analytical rules (Blast Radius, Risk Scoring). Contains NO framework code or SQL.
    *   **Application Layer:** Contains use cases and service interfaces (e.g., IngestionService).
    *   **Infrastructure Layer:** Implements adapters (SQLAlchemy, Snowflake-Connector, SQLite) and controllers.

### 3. Interface-Driven & Mockable
*   **The Law:** Dependency inversion must be used for all external resources. High-level modules must depend on abstractions (interfaces), never on concrete classes.
*   **The Implementation:** Connectors, search backends, and storage adapters must be defined using strict interfaces (e.g., AbstractConnector, MetadataRepository). Mocks must be created for every interface to ensure the application can run and be unit-tested without connecting to a live database or cloud warehouse.

### 4. No Business Logic in Controllers
*   **The Law:** Controllers (such as FastAPI route handlers) are strictly entry-points responsible for HTTP validation, authorization, routing, and response serialization.
*   **The Implementation:** Route handlers must delegate all business logic to application services or domain entities. If a route handler contains SQL queries, conditional business rules, or mathematical formulas, it is a constitutional violation.

### 5. Plugin-First Connector Architecture
*   **The Law:** Adding support for new data platforms (BigQuery, Tableau, etc.) must not modify the core metadata model or core engine code.
*   **The Implementation:** All data connectors must exist as isolated pluggable modules that implement the core connector interface. The engine discovers and registers plugins at startup. Adding a connector must only require writing code in a self-contained directory under the plugin namespace.

### 6. Security by Default
*   **The Law:** Metadata is highly sensitive, and database access credentials must be handled with extreme security.
*   **The Implementation:**
    *   Credentials must be encrypted at rest using AES-256 in CBC mode with HMAC verification, utilizing a master key provided exclusively via environment variables.
    *   Passwords, passphrases, and key strings must never be logged or output in error messages.
    *   The SQL parser must omit actual query constants/values to prevent sensitive data leak in metadata logs.

### 7. Test-Driven Development (TDD)
*   **The Law:** No feature is complete without comprehensive test coverage.
*   **The Implementation:** Every backend service must have unit tests covering normal operations, edge cases, and failure modes. The master branch must maintain >80% code coverage. If a PR lacks unit tests for new logic, it cannot be merged.

---

## Violation Examples & Refactoring Guide

### Violations vs Correct Implementations

#### Example A: In-line SQL in Controllers
*   ❌ **Violating Code:**
    ```python
    @app.get("/api/v1/tables")
    def get_tables():
        # Violation: SQL query directly inside HTTP route handler!
        db = get_db_connection()
        return db.execute("SELECT * FROM metadata_tables").fetchall()
    ```
*   ✔ **Correct Code:**
    ```python
    @app.get("/api/v1/tables", response_model=List[TableSchema])
    def get_tables(service: TableService = Depends(get_table_service)):
        # Correct: Delegate to domain service layer
        return service.list_active_tables()
    ```

#### Example B: Tight Coupling to a Vendor API
*   ❌ **Violating Code:**
    ```python
    class SyncPipeline:
        def execute(self):
            # Violation: Tied directly to Snowflake connector! Can't test offline.
            conn = snowflake.connector.connect(...)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
    ```
*   ✔ **Correct Code:**
    ```python
    class SyncPipeline:
        def __init__(self, connector: IConnector):
            # Correct: Program against an interface, inject dependencies
            self.connector = connector
            
        def execute(self):
            metadata = self.connector.fetch_schema()
    ```
