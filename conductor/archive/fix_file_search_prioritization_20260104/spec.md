# Specification: Fix File Search Prioritization and Formatting

## Overview
This track addresses a regression in the agent's behavior where the file search tool is not being prioritized as effectively as before. This is attributed to two factors:
1.  **Formatting Bug:** The code appending the file search instruction lacks a leading newline, causing it to concatenate improperly with the previous system instruction (e.g., `...Google SearchIMPORTANT...`).
2.  **Instruction Strength:** The new generic instruction is less forceful than the original Dazbo-specific instruction, lacking the `required_action` keyword and the explicit directive to "start by searching".

## Functional Requirements

### 1. Fix Formatting Bug
-   Modify `src/rickbot_agent/agent.py` to ensure a newline is added before appending the file search instruction.

### 2. Strengthen Generic Instruction
-   Update the generic file search instruction in `src/rickbot_agent/agent.py` to restore the strictness of the original implementation.
-   **New Instruction Text:**
    ```text
    IMPORTANT: required_action: You MUST start by searching your reference materials using the 'file_search' tool for information relevant to the user's request.
    Always use the 'file_search' tool before answering.
    ```

### 3. Verification
-   Verify the fix by running existing unit tests (which check for the presence of the instruction string).
-   Update the unit tests to match the new instruction text.

## Non-Functional Requirements
-   Maintain the generic nature of the implementation (no hardcoded personality names).

## Out of Scope
-   Configuration flags for instruction strictness (Option A selected: Permanently strengthen for all).
