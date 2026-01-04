# Specification: Generic File Search Store Configuration

## Overview
This feature generalizes the File Search Store configuration in the Rickbot agent. Currently, file search capabilities are hardcoded specifically for the "Dazbo" personality. This change will allow *any* personality to have an associated File Search Store configured via the `personalities.yaml` file, removing the Dazbo-specific technical debt and enabling a more flexible RAG (Retrieval Augmented Generation) architecture.

## Functional Requirements

### 1. YAML Configuration
-   Update `src/rickbot_agent/data/personalities.yaml` to support an optional `file_search_store_id` field for each personality.
-   **Example:**
    ```yaml
    - name: "Dazbo"
      # ... other fields ...
      file_search_store_id: "projects/123/locations/us-central1/stores/abc-456"
    ```

### 2. Personality Class Update
-   Update the `Personality` dataclass in `src/rickbot_agent/personality.py` to include the optional `file_search_store_id` field.
-   Ensure this field defaults to `None` or an empty string if not present in the YAML.

### 3. Agent Logic Generalization
-   Modify `src/rickbot_agent/agent.py` to remove `if personality.name == "Dazbo":` checks.
-   Instead, check if `personality.file_search_store_id` is populated.
-   If populated:
    -   Inject the `file_search` tool into the model request.
    -   Append a generic system instruction: *"You have access to reference materials via the 'file_search' tool. Use it to provide accurate information based on the provided context."*

### 4. Configuration Cleanup
-   Remove `dazbo_file_search_store_name` from `src/rickbot_utils/config.py`.
-   Remove references to `DAZBO_FILE_SEARCH_STORE_NAME` environment variable in the code (but update `.env` to reflect the new generic usage if necessary, or just rely on the YAML).

### 5. Testing
-   Update integration tests in `src/tests/` that rely on Dazbo's specific file search behavior to use the new generic mechanism.
-   Ensure tests pass for both personalities with and without a file search store.

## Non-Functional Requirements
-   **Backward Compatibility:** The existing behavior for Dazbo should remain functional (user can manually move the ID from env var to YAML).
-   **Security:** Ensure no sensitive IDs are committed if they are truly sensitive (though Store IDs are generally resource identifiers).

## Out of Scope
-   Creating new File Search Stores (managed via notebook).
-   UI changes.
