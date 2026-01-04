# Plan: Generic File Search Store Configuration

## Phase 1: Data Model & Configuration Generalization [checkpoint: ec3af63]

- [x] Task: Update `Personality` dataclass in `src/rickbot_agent/personality.py` to include `file_search_store_id: str | None = None`.

- [x] Task: Update `src/rickbot_agent/data/personalities.yaml` to include `file_search_store_id` for Dazbo (migrating it from the environment variable value).

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)



## Phase 2: Agent Logic Refactoring

- [ ] Task: Write failing unit tests in `src/tests/unit/test_agent_generic_search.py` to verify that an agent with `file_search_store_id` in its personality automatically attaches the tool and instruction.

- [ ] Task: Modify `src/rickbot_agent/agent.py` to use the generic `personality.file_search_store_id` instead of Dazbo-specific hardcoding.

- [ ] Task: Implement the generic system instruction injection for personalities with a search store.

- [ ] Task: Verify that the tests pass and coverage is maintained.

- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)



## Phase 3: Integration & Cleanup

- [ ] Task: Update existing integration tests (e.g., `src/tests/integration/test_tool_status.py`) to ensure they still pass with the new configuration mechanism.

- [ ] Task: Remove `dazbo_file_search_store_name` from `src/rickbot_utils/config.py` and remove associated environment variable loading logic.

- [ ] Task: Remove `DAZBO_FILE_SEARCH_STORE_NAME` from `.env` and `.env.local.example`.

- [ ] Task: Final project-wide linting and spellcheck.

- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
