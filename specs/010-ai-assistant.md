# Specification: 010 - AI Assistant

## Overview
This specification details the LLM-powered AI Assistant for ImpactGraph. The assistant translates complex lineage sub-graphs, schema definitions, and dependency structures into natural language explanations. It helps users trace structural risks and query the metadata repository using standard English.

---

## Problem Statement
While data platform engineers can easily navigate graph networks, business analysts and less-technical stakeholders struggle to interpret raw lineage DAGs or complex SQL view definitions. We need an AI assistant that can digest graph contexts and explain dependencies, risks, and ownership paths in plain language.

---

## Goals
*   Integrate with LLM providers (OpenAI, Claude, or local Ollama instances) using standard APIs.
*   Generate natural language summaries of any metadata asset's lineage and schema.
*   Explain the downstream blast radius and risk factors of altering a specific column.
*   Provide a natural language metadata search interface (e.g., *"Where does our customer email data come from?"*).
*   Enforce security filters to prevent database credentials from leaking into LLM prompt contexts.

---

## User Stories
1.  **As a Data Analyst**, I want to click "Explain Lineage" on a dashboard view and receive a summary: *"This view combines user account names from RAW_USERS with monthly transaction sums from FACT_ORDERS."*
2.  **As a Compliance Auditor**, I want to ask: *"Which views process customer email addresses?"* and see a list of matching metadata nodes.
3.  **As an Analytics Engineer**, I want the AI to write a summary explaining why a table is rated as "High Risk".

---

## Functional Requirements
*   **FR-1:** LLM Client Setup: Integrate an OpenAI-compatible client library that connects to external models (e.g., gpt-4o, claude-3-sonnet) using an `OPENAI_API_KEY` or `OLLAMA_HOST` env variable.
*   **FR-2:** Contextual Prompt Builder: Automatically compile metadata schemas (table descriptions, column lists, and parent/child lineages) into structured system prompts.
*   **FR-3:** Lineage Explainer: Traverse the NetworkX graph cache to extract upstream/downstream paths and prompt the LLM to explain the data flow steps.
*   **FR-4:** Risk Summarizer: Take a `risk_scores` payload and view code strings and summarize why an object is flagged (e.g., outlining specific deleted tables).
*   **FR-5:** Token & Prompt Redaction: Parse prompt contexts to redact database passwords, keys, or sensitive schema comments before payload transmission.

---

## UI Requirements
*   **AI Assistant Chat Drawer:** A collapsible panel on the right side of the screen. Includes:
    *   **Chat History:** Clean bubble text bubbles distinguishing between user input and assistant markdown responses.
    *   **Contextual Chips:** Quick-action buttons: *"Explain Lineage"*, *"Summarize Risk"*, *"Find Owners"*.
    *   **Inline Explainer Widgets:** Small "Explain with AI" buttons next to view code containers and lineage graph edges.

---

## Backend Requirements
*   **Service Class:** `AiAssistantService` managing prompts, redacting secrets, and executing API calls.
*   **Connector SDK:** `openai` python package (fully compatible with local Ollama endpoints).

---

## Database Changes
No new tables required. This specification operates on the existing metadata and risk tables.

---

## API Endpoints

### 1. Contextual Chat
*   `POST /api/v1/ai/chat`
    *   **Request Body:**
        ```json
        {
          "message": "Why is customer_summary marked as High Risk?",
          "context_object_id": "uuid",
          "context_object_type": "TABLE"
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
          "response": "The `customer_summary` view is marked as High Risk (Score: 90) because it queries the table `RAW_USERS` which was deleted by SALES_OPS during this morning's sync. This views is currently broken (Dead View) and has 8 downstream reports affected.",
          "sources_referenced": ["RAW_USERS", "CUSTOMER_SUMMARY"]
        }
        ```

### 2. Lineage Narrative Explainer
*   `POST /api/v1/ai/explain/lineage`
    *   **Request Body:** `{"table_id": "uuid"}`
    *   **Response (200 OK):**
        ```json
        {
          "summary": "This view aggregates transactional data. It selects the customer ID from CUSTOMERS, joins it with transaction details from FACT_TRANSACTIONS, and computes monthly sales sums.",
          "upstream_paths_count": 2
        }
        ```

---

## Example Contextual Prompt Template
When explaining a table's lineage, the backend compiles this context for the LLM:
```text
System Prompt:
You are an expert data catalog assistant. Explain the lineage and purpose of the target table.
Target Table: [table_name] (Type: [type])
Description: [description]
Columns: [list of columns with types]

Direct Upstream Tables:
- [parent_table_1] (Columns: [cols])
- [parent_table_2] (Columns: [cols])

Direct Downstream Tables:
- [child_table_1] (Columns: [cols])

Explain how data flows from the parent tables into the target table, and what the downstream impact is. Keep the explanation concise and professional.
```

---

## Acceptance Criteria
1.  Sending a lineage explanation request returns a structured text summary written in clean markdown format.
2.  If the external LLM provider API is offline or returns an error, the backend falls back gracefully to a static template description without throwing a server error.
3.  Unit tests verify that prompt generation redacts passwords or secret keys.
4.  Standard markdown files successfully render AI chat summaries.

---

## Out of Scope
*   Training or fine-tuning custom LLM models locally in this repository.
*   Allowing the AI assistant to write database DDL migration code directly.

---

## Future Enhancements
*   Translating English commands into SQL queries using SQL generation models.
*   Voice-to-text inputs.

---

## Dependencies
*   Spec 001 - Project Foundation
*   Spec 003 - Metadata Engine (schema inputs).
*   Spec 005 - Lineage (graph pathways).
*   Spec 006 - Impact Analysis (risk metrics).
