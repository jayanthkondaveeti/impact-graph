# Brainstorm: Future Feature Backlog

This document captures future feature ideas for the ImpactGraph platform. These ideas are outside the MVP scope and can be graduated into proper specifications in future sprints.

---

## 1. Schema Validation CLI
A command-line tool that developers can run in their local terminal or during pre-commit hooks to validate if their local DDL changes will break downstream production views.
*   **Command:** `impactgraph validate --ddl-file migrations/v2_add_discount.sql`
*   **Operation:** Sends the local SQL file to the ImpactGraph API. The API parses the SQL, merges it temporarily into the graph cache, calculates the impact diff, and returns warnings or blocks the commit.

---

## 2. Interactive Schema Data Diffing
Provide a "Diff" tab on the table details page to visually compare schema states between two points in time.
*   **Use Case:** *"Show me what changed in the FACT_TRANSACTIONS table schema between last Friday and today."*
*   **UI:** GitHub-style split-pane view showing columns added (green highlight), removed (red strikeout), or type-modified.

---

## 3. Auto-Tagging & PII Classification Heuristics
Automatically tag columns that contain sensitive personal data (PII) using regex search heuristics during metadata syncs.
*   **Rules:**
    *   If column name contains `ssn`, `social_security`, or matches regex `\b\d{3}-\d{2}-\d{4}\b` in descriptions ➔ Tag `#PII-SSN`.
    *   If column name contains `email`, `mail_addr` ➔ Tag `#PII-EMAIL`.
    *   If column name contains `phone`, `tel` ➔ Tag `#PII-PHONE`.
*   **Downstream Tag Propagation:** Automatically propagate tags downstream. If `RAW_USERS.email` is tagged `#PII-EMAIL`, any view selecting from it inherits the tag.

---

## 4. Lineage Catalog Version Control
Treat lineage mapping like code by maintaining a history of changes. Allow restoring previous versions of the lineage graph to debug when an edge was deleted.

---

## 5. In-App Metadata Editing (Data Cataloging)
Provide a wiki-like markdown editor on the table/column details page so database owners can write documentation, add notes, and assign tags directly in ImpactGraph, which is stored in Postgres without modifying the raw database comments.
