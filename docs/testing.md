# Unified Testing Documentation

This document serves as the comprehensive guide for testing strategy, execution, and manual verification for the Rickbot-ADK project.

## Table of Contents
1. [Backend Testing Strategy](#backend-testing-strategy)
   - [Test Summary](#test-summary)
   - [Configuration & Test Mode](#configuration--test-mode)
   - [Running Backend Tests](#running-backend-tests)
2. [Frontend Testing Strategy](#frontend-testing-strategy)
   - [Stack Overview](#stack-overview)
   - [Running Frontend Tests](#running-frontend-tests)
3. [Authentication & Session Management](#authentication--session-management)
   - [Retrieving Bearer Tokens](#retrieving-bearer-tokens)
   - [Mock Tokens](#mock-tokens)
4. [Manual API Verification](#manual-api-verification)
   - [Using Curl with Authentication](#using-curl-with-authentication)
   - [Artifact Retrieval](#artifact-retrieval)

---

## Backend Testing Strategy

This section covers the strategy for testing the Python backend components of the Rickbot-ADK project.

### Test Summary

The following table summarizes the existing backend tests, their category, and their purpose:

| File | Category | Purpose |
| :--- | :--- | :--- |
| `test_config.py` | Unit | Verifies the loading and validation of application configuration from `config.py`. |
| `test_create_auth_secrets.py` | Unit | Tests the utility script for creating Streamlit authentication secrets. |
| `test_logging_utils.py` | Unit | Validates the setup and functionality of the logging utilities. |
| `test_personality.py` | Unit | Tests the `Personality` data class and ensures personalities are loaded correctly from the YAML configuration. |
| `test_auth_models.py` | Unit | Tests the `AuthUser` Pydantic model for user authentication data. |
| `test_auth_dependency.py` | Unit | Verifies the token validation logic, including mock token support. |
| `test_artifacts.py` | Integration | Verifies that file uploads are saved as ADK Artifacts and can be retrieved via the `/artifacts` endpoint. |
| `test_tool_status.py` | Integration | Verifies that tool call events are correctly emitted by the `/chat_stream` endpoint. |
| `test_api.py` | Integration | Contains tests for the FastAPI `/chat` endpoint. Includes a mocked test for basic success and a true integration test for multi-turn conversation memory. |
| `test_personalities.py` | Integration | Runs a simple query against every available agent personality to ensure each one can be loaded and can respond. |
| `test_rickbot_agent_multiturn.py` | Integration | Verifies the agent's conversation memory by directly using the ADK `Runner` for a two-turn conversation. |
| `test_server_e2e.py` | Integration (E2E) | Provides an end-to-end test by starting the actual FastAPI server via `uvicorn` and testing endpoints like `/chat` and `/chat_stream`. |

### Configuration & Test Mode

To ensure tests can run without requiring production secrets (specifically those for "Dazbo" or other protected personalities), the test suite runs in **Test Mode**.

- **Mechanism**: The `RICKBOT_TEST_MODE` environment variable is set to `"true"` automatically for all tests via `src/tests/conftest.py`.
- **Behavior**: When `RICKBOT_TEST_MODE` is active, if the application fails to retrieve a system prompt secret from Google Secret Manager, it falls back to a dummy system prompt (`"You are {name}. (DUMMY PROMPT FOR TESTING)"`) instead of raising a `ValueError`.
- **Purpose**: This ensures that unit and integration tests (such as `test_personalities.py`) do not crash due to missing local secrets or permissions, while still allowing the actual logic to be exercised.

#### Conftest

The `src/tests/conftest.py` file is a global Pytest configuration that:
1.  Sets `RICKBOT_TEST_MODE=true` for the entire test session.
2.  Ensures consistent environment variables are available for both unit and integration tests.

### Running Backend Tests

- We can run backend tests with:
  ```bash
  make test # unit tests only
  make test-all # all tests
  ```

- **CI Environment Variable:** Setting `CI=true` is recommended when running tests in a CI/CD pipeline or as a non-interactive agent. It ensures that test runners (like `pytest`) run in a single-execution mode rather than a "watch" or "interactive" mode, and it can also be used to suppress interactive prompts or local-only configurations.
- Note that integration tests will fail if the development environment has not first been configured with the `setup-env.sh` script. This is because the test code will not have access to the required Google APIs.

#### Testing with Verbose Output

If we want to run tests verbosely, we can do this:

```bash
uv run pytest -v -s src/tests/unit/test_config.py
uv run pytest -v -s src/tests/unit/test_personality.py
uv run pytest -v -s src/tests/integration/test_rickbot_agent_multiturn.py
uv run pytest -v -s src/tests/integration/test_server_e2e.py
uv run pytest -v -s src/tests/integration/test_personalities.py
```

## Frontend Testing Strategy
*(Pending implementation)*

## Authentication & Session Management
*(Pending implementation)*

## Manual API Verification
*(Pending implementation)*
