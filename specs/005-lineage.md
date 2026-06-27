# Specification: 005 - Lineage

## Overview
This specification details the interactive Lineage visualization component of ImpactGraph. The visualizer maps and renders table-level and column-level data relationships in a directed acyclic graph (DAG), enabling engineers to trace the flow of data through their warehouse.

---

## Problem Statement
Tracing how data moves from raw source tables, through staging views, to final analytical aggregates is difficult to do in text form. Users need a visual, interactive graph explorer that represents these dependencies, allows toggling between table and column details, and provides quick navigation along upstream and downstream pathways.

---

## Goals
*   Render table-level dependency nodes and directional edges in a left-to-right flow.
*   Expose column-level mapping overlays when expanding a table node.
*   Support interactive canvas operations (zoom, pan, drag-and-drop, fit-to-canvas).
*   Highlight lineage path highlights (fade out unrelated nodes when focusing on a specific node or column).
*   Expose high-performance path traversal APIs utilizing the `NetworkX` in-memory cache.

---

## User Stories
1.  **As a Data Engineer**, I want to click a table in the graph and see all upstream tables highlight in green and downstream views highlight in red.
2.  **As an Analytics Engineer**, I want to select a specific column (e.g., `user_id`) and isolate only the path of columns that feed into it across multiple views.
3.  **As an Auditor**, I want to click on a lineage node and open a sidebar containing schema details, owner, and direct dependencies without leaving the canvas.

---

## Functional Requirements
*   **FR-1:** Table Lineage: Retrieve and render all direct and indirect dependencies (parents/children) for a target table up to a user-defined degree of separation (default: 3).
*   **FR-2:** Column Lineage: Resolve and render specific column-to-column pathways. Highlighting a column must highlight its ancestral source columns and descendant targets.
*   **FR-3:** Interactive Canvas: Build the frontend graph using the `React Flow` library, allowing standard zoom, pan, and dragging behaviors.
*   **FR-4:** Path Traversal Engine: Utilize NetworkX algorithms (`ancestors()`, `descendants()`) to extract sub-graphs for lineage queries quickly.
*   **FR-5:** Sidebar Metadata Integration: Display quick-stats (owner, table type, description, row count) in a slide-out panel when a graph node is clicked.

---

## UI Requirements
*   **Interactive Graph Canvas:**
    *   Left-to-right hierarchical tree layout (DAG).
    *   Custom nodes indicating platform (Snowflake logo), type (Table = Blue icon, View = Purple icon), and name.
    *   Expandable column drawer inside table nodes, listing columns with data types.
    *   Control bar: Zoom In/Out, Fit View, Lock Node Positions, Clear Highlights.
*   **Details Sidebar:** Slides out from the right when a node is clicked. Contains links to full schema details, a copy identifier button, and lists of direct parents/children.

---

## Backend Requirements
*   **API Schema:** Standardized JSON nodes and edges structure:
    ```typescript
    interface LineageGraph {
      nodes: { id: string; label: string; type: string; details: any }[];
      edges: { id: string; source: string; target: string; type: string }[];
    }
    ```
*   **Graph Traversal Service:** Calls `networkx.subgraph()` using the cached database dependency edges.

---

## Database Changes
No new tables required. This specification queries the `dependencies`, `tables`, and `columns` tables created in Spec 001 and Spec 003.

---

## API Endpoints

### 1. Table Lineage Graph
*   `GET /api/v1/lineage/table/{id}`
    *   **Parameters:**
        *   `direction` (Optional, 'upstream', 'downstream', or 'both')
        *   `depth` (Optional, integer, default 3)
    *   **Response (200 OK):**
        ```json
        {
          "nodes": [
            { "id": "table-1", "label": "RAW_USERS", "type": "TABLE", "is_anchor": true },
            { "id": "table-2", "label": "SECURE_USERS_VIEW", "type": "VIEW", "is_anchor": false }
          ],
          "edges": [
            { "id": "edge-1", "source": "table-1", "target": "table-2", "type": "table_to_table" }
          ]
        }
        ```

### 2. Column Lineage Graph
*   `GET /api/v1/lineage/column/{id}`
    *   **Response (200 OK):**
        ```json
        {
          "nodes": [
            { "id": "col-1", "label": "cust_id", "table_id": "table-1" },
            { "id": "col-2", "label": "customer_uuid", "table_id": "table-2" }
          ],
          "edges": [
            { "id": "edge-col-1", "source": "col-1", "target": "col-2", "type": "column_to_column" }
          ]
        }
        ```

---

## Acceptance Criteria
1.  Entering a table details page and clicking "View Lineage" loads a graph showing correct upstream and downstream tables.
2.  Expanding a table node renders its columns list; clicking a column handle triggers the column lineage API and highlights matching paths.
3.  The graph layout runs smoothly (maintains 60fps) for schemas up to 200 nodes on common modern browsers.
4.  Sub-graph extraction logic is covered by unit tests validating correctness of parents/children lists in NetworkX.

---

## Out of Scope
*   Dynamically adding or deleting database columns directly inside the graph interface.
*   Integrating external data catalog integrations (e.g. Alation, Collibra) in this spec.

---

## Future Enhancements
*   Adding SQL statement preview tooltip over lineage edges.
*   Exporting lineage graphs as vector SVG files.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 003 - Metadata Engine (dependency schema & view parser).
