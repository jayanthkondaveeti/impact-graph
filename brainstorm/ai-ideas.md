# Brainstorm: AI & LLM Integration Ideas

This document captures advanced artificial intelligence and large language model ideas for ImpactGraph.

---

## 1. Natural Language to SQL Translation for Metadata Queries
Allow users to query the metadata repository using standard English, translating their inputs into PostgreSQL queries that run against our database.
*   **Example Input:** *"Which tables in schema PUBLIC have not been synced in the last week?"*
*   **Translated SQL:**
    ```sql
    SELECT t.name, s.name 
    FROM tables t 
    JOIN schemas s ON t.schema_id = s.id 
    JOIN sync_jobs j ON t.database_id = j.database_id 
    WHERE s.name = 'PUBLIC' AND j.completed_at < NOW() - INTERVAL '7 days';
    ```
*   **Benefit:** Zero need to teach business users SQL schemas or database structures.

---

## 2. Automated DDL Patch Generators (Auto-Fix)
When a schema change is proposed (e.g. renaming column `user_email` to `email`), the AI assistant parses the downstream views and automatically generates SQL patch scripts to correct all downstream queries.
*   **Input:** Column change request.
*   **Process:** AI reads the current view definition SQL strings from downstream objects, substitutes the column identifier, validates syntax, and writes a list of DDL patch statements.
*   **Result:** Outputs a single `.sql` script containing the exact statements needed to roll out the refactoring without breaking any dependencies.

---

## 3. Fine-Tuning LLMs on Lineage and View Definitions
Create open-source, lightweight fine-tuning datasets (e.g., for Llama-3-8B or Mistral-7B) containing pairs of:
*   **Prompt:** SQL DDL view statements.
*   **Response:** Structured JSON lists of dependencies.
*   **Benefit:** Allows companies to run a small local LLM inside their private network that parses SQL lineage with high accuracy, completely eliminating the need for outbound OpenAI or Claude API calls.

---

## 4. Conversational Slack/Teams Bot
A bot that listens in engineering channels or can be queried directly:
*   **Query:** `/impactgraph blast-radius CUSTOMERS`
*   **Response:** *"FACT_SALES and 12 dashboards will be affected by this change. The owner is Elena."*
