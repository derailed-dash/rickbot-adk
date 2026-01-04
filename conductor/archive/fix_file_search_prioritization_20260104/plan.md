# Plan: Fix File Search Prioritization and Formatting

## Phase 1: Implementation & Verification [checkpoint: dafca20]
- [x] Task: Update `src/tests/unit/test_agent_generic_search.py` to expect the new, stricter instruction text and checking for the newline.
- [x] Task: Modify `src/rickbot_agent/agent.py` to add the leading newline and update the instruction text.
- [x] Task: Verify that `uv run pytest src/tests/unit/test_agent_generic_search.py` passes.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)
