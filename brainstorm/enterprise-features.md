# Brainstorm: Enterprise Features & Governance

This document outlines security, scale, and compliance features required for enterprise adoption of ImpactGraph.

---

## 1. Federated Single Sign-On (OIDC / SAML 2.0)
*   **Goal:** Integrate authentication with enterprise identity providers (Okta, Azure AD, Ping Identity).
*   **Mechanism:** Use `authlib` to support OpenID Connect (OIDC) flow. Securely map AD user groups to default admin or read-only roles inside ImpactGraph.

---

## 2. Row & Column-Level Metadata Access Control (SSO RBAC)
*   **Goal:** Restrict which tables or databases a user can view in the ImpactGraph portal.
*   **Rationale:** Even if data values are hidden, metadata alone (such as payroll table schemas or billing column names) is highly sensitive.
*   **Mechanism:** Filter search queries and graph renderings based on the user's mapped group permissions. A user belonging to the `Marketing` AD group should only see marketing-related database assets in the search explorer.

---

## 3. Compliance Audit Logging & Splunk Integration
*   **Goal:** Log every search query, lineage view, and config edit to satisfy security audits.
*   **Mechanism:** Write audit logs to PostgreSQL and stream them in standard JSON format to Splunk, Datadog, or AWS CloudWatch.
*   **Alerting:** Trigger alerts if a user queries the lineage of sensitive tables (e.g. `SALARIES`) more than 10 times in an hour.

---

## 4. Multi-Tenant Organization Workspaces
*   **Goal:** Allow a single parent company instance of ImpactGraph to manage isolated workspaces for different business units.
*   **Mechanism:** Add an `organization_id` column to all metadata tables and enforce row-level security (RLS) policies in PostgreSQL.
