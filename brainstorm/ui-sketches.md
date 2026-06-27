# Brainstorm: UI Layouts & Sketches

This document contains interface layout concepts, layout structures, and ASCII wireframes for the ImpactGraph web portal.

---

## 1. Global Search Autocomplete Dropdown
This wireframe shows how search suggestions should render in a floating overlay container under the header input.

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Search database assets... [ typed: "cust" ]                       🔎  │
├────────────────────────────────────────────────────────────────────────┤
│ Suggestions:                                                           │
│  [Table]  CUSTOMERS            path: PROD_DB.SALES.CUSTOMERS           │
│  [Table]  CUSTOMER_ADDRESS     path: PROD_DB.SALES.CUSTOMER_ADDRESS    │
│  [View ]  CUSTOMER_REPORTS     path: PROD_DB.PUBLIC.CUSTOMER_REPORTS   │
│  [Column] cust_id (INT)        table: FACT_SALES                       │
├────────────────────────────────────────────────────────────────────────┤
│ Press [Enter] for advanced search results with filters.                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Interactive Lineage Canvas Workspace
A three-column layout maximizing canvas surface area while retaining context controls.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Header: Title / Ingest Status (Green)                 🔎 Global Search │
├───────────────┬────────────────────────────────────────┬───────────────┤
│               │ Canvas Workspace                       │               │
│ Left Panel    │                                        │ Right Panel   │
│ (Navigation)  │    [ Table A ] ────┐                   │ (Details)     │
│               │                    ▼                   │               │
│ - Dashboard   │    [ Table B ] ───➔ [ View C ] ➔ [Tab] │ Name: View C  │
│ - Search      │                    ▲                   │ Type: View    │
│ - Lineage     │    [ Table D ] ────┘                   │ Owner: Elena  │
│ - Security    │                                        │ Risk Score: 12│
│ - Settings    │                                        │               │
│               │ ┌────────────────────────────────────┐ │ [ Upstreams ] │
│               │ │ Controls: [ + ] [ - ] [ Fit ] [🎨] │ │ - Table B     │
│               │ └────────────────────────────────────┘ │ - Table D     │
└───────────────┴────────────────────────────────────────┴───────────────┘
```

---

## 3. RBAC Access Explorer Paths Tree
Shows how privilege flow paths should render inside the access details modal.

```text
┌─────────────────────────────────────────────────────────────┐
│  Role Access Inheritance Path Trace                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    [ User: johndoe ]                                        │
│           │ (member of)                                     │
│           ▼                                                 │
│    [ Role: FIN_ANALYST ]                                    │
│           │ (grants inherited by)                           │
│           ▼                                                 │
│    [ Role: FIN_LEAD ]                                       │
│           │ (has explicit grant)                            │
│           ▼                                                 │
│    [ Privilege: SELECT on table FACT_TRANSACTIONS ]         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                [ Close ]    │
└─────────────────────────────────────────────────────────────┘
```
