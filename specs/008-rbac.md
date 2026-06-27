# Specification: 008 - RBAC Visualization

## Overview
This specification details the Role-Based Access Control (RBAC) Explorer and Security Visualizer for ImpactGraph. The explorer maps Snowflake role hierarchies, resolves inherited privileges, and traces access pathways from individual users to specific schema columns.

---

## Problem Statement
Understanding data authorization in Snowflake is difficult because privileges inherit through nested role trees (e.g., `USER ➔ ROLE_A ➔ ROLE_B ➔ TABLE`). Security teams struggle to audit who has access to sensitive tables or PII columns, leading to compliance risks. We need an access explorer that visualizes these privileges and role hierarchies.

---

## Goals
*   Visualize the Snowflake role hierarchy as an interactive tree diagram.
*   Resolve inherited permissions (calculate all users and roles who can read or write to a target table).
*   Trace the exact path of role inheritance explaining *why* a user has access to a table.
*   Provide a "User Access Audit" search to list all tables a specific user is authorized to read.

---

## User Stories
1.  **As a Security Compliance Officer**, I want to select the `SALES_PAYMENTS` table and see a list of all users who can access it, grouped by their direct and inherited roles.
2.  **As a Database Administrator**, I want to visualize our role inheritance tree to verify that our `ANALYTICS_READ` role does not inherit administrative `ACCOUNTADMIN` rights.
3.  **As an Auditor**, I want to search for user "John Doe" and list every database schema he has privilege to query.

---

## Functional Requirements
*   **FR-1:** Role Graph Construction: Build a directed role-inheritance graph where nodes are Roles/Users and edges represent memberships (`grant role A to role B`).
*   **FR-2:** Access Resolution: For a target table `T`, crawl the roles graph to find:
    *   Roles with direct grants (e.g., `SELECT` on `T`).
    *   All ancestor roles in the hierarchy that inherit that grant.
    *   All users assigned to any of these direct or inherited roles.
*   **FR-3:** User Privilege Mapping: For a target user `U`, resolve all active privileges by traversing down all roles the user belongs to, compiling a list of readable database tables.
*   **FR-4:** Path Trace Explainer: Return a structured array showing the grant chain (e.g., `John Doe ➔ FIN_ANALYST ➔ FIN_LEAD ➔ SELECT on PAYMENTS_TABLE`).

---

## UI Requirements
*   **Access Explorer Tab:** Located on the table details view. Includes:
    *   **Authorized Users List:** A table listing Username, Assigned Role, Access Type (Direct or Inherited), and the **Inheritance Path** trigger button.
    *   **Access Path Modal:** A small popup rendering a vertical chain representing the role grants path.
*   **Security Explorer Panel:**
    *   Dedicated explorer workspace to search by User or Role.
    *   Canvas rendering the role inheritance tree.

---

## Backend Requirements
*   **Algorithm Logic:** Use NetworkX directed graph algorithms to compute paths between Users and Roles:
    *   `networkx.shortest_path(role_graph, source_user, target_role)` to trace the inheritance path.
*   **Security Service:** `RbacService` handling database queries and graph merges.

---

## Database Changes
No new tables required. This specification operates on the `roles`, `role_inheritance`, `privileges`, `users`, and `user_roles` database tables.

---

## API Endpoints

### 1. Object Access Audit
*   `GET /api/v1/rbac/tables/{id}/access`
    *   **Response (200 OK):**
        ```json
        {
          "table_id": "uuid",
          "table_name": "FACT_PAYMENTS",
          "direct_grants": [
            { "role_name": "FIN_LEAD", "privilege_type": "SELECT" }
          ],
          "authorized_users": [
            {
              "username": "johndoe",
              "effective_role": "FIN_LEAD",
              "grant_type": "INHERITED",
              "inheritance_path": ["johndoe", "FIN_ANALYST", "FIN_LEAD", "FACT_PAYMENTS"]
            }
          ]
        }
        ```

### 2. Global Role Hierarchy Graph
*   `GET /api/v1/rbac/roles/hierarchy`
    *   **Response (200 OK):**
        ```json
        {
          "nodes": [
            { "id": "role-admin", "label": "ACCOUNTADMIN", "type": "ROLE" },
            { "id": "role-analyst", "label": "FIN_ANALYST", "type": "ROLE" }
          ],
          "edges": [
            { "source": "role-analyst", "target": "role-admin" }
          ]
        }
        ```

### 3. User Privilege List
*   `GET /api/v1/rbac/users/{username}/privileges`
    *   **Response (200 OK):**
        ```json
        {
          "username": "johndoe",
          "assigned_roles": ["FIN_ANALYST"],
          "authorized_tables": [
            {
              "table_id": "uuid",
              "table_name": "FACT_SALES",
              "privilege": "SELECT"
            }
          ]
        }
        ```

---

## Acceptance Criteria
1.  Querying a table's access correctly identifies users who inherit access through multiple levels of role nesting.
2.  Role hierarchy endpoint returns clean node/edge structures compatible with frontend graph libraries.
3.  Privilege lookup queries for users resolve in under `150ms` for graphs containing up to 1,000 roles.
4.  Credentials and passwords are excluded from the output payloads.

---

## Out of Scope
*   Modifying Snowflake roles or granting privileges (read-only audit dashboard).
*   Enforcing database row-level security policies inside the ImpactGraph application itself.

---

## Future Enhancements
*   Flagging excessive privileges (e.g. users holding ADMIN roles who have not run queries in 90 days).
*   Highlighting roles violating security rules (e.g., circular role dependencies).

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 002 - Snowflake Connector (RBAC sync details).
