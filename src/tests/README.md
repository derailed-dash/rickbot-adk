# Testing Guidance

This document provides guidance on the testing strategy for the Rickbot-ADK project.

## Test Summary

The following table summarizes the existing tests, their category, and their purpose:

| File | Category | Purpose |
| :--- | :--- | :--- |
| `test_config.py` | Unit | Verifies the loading and validation of application configuration from `config.py`. |
| `test_create_auth_secrets.py` | Unit | Tests the utility script for creating Streamlit authentication secrets. |
| `test_logging_utils.py` | Unit | Validates the setup and functionality of the logging utilities. |
| `test_personality.py` | Unit | Tests the `Personality` data class and ensures personalities are loaded correctly from the YAML configuration. |
| `test_auth_models.py` | Unit | Tests the `AuthUser` Pydantic model for user authentication data. |
| `test_auth_dependency.py` | Unit | Verifies the token validation logic, including mock token support. |
| `AuthButton.test.tsx` | Unit (Frontend) | Tests the `AuthButton` React component using Jest and React Testing Library. |
| `test_api.py` | Integration | Contains tests for the FastAPI `/chat` endpoint. Includes a mocked test for basic success and a true integration test for multi-turn conversation memory. |
| `test_personalities.py` | Integration | Runs a simple query against every available agent personality to ensure each one can be loaded and can respond. |
| `test_rickbot_agent_multiturn.py` | Integration | Verifies the agent's conversation memory by directly using the ADK `Runner` for a two-turn conversation. |
| `test_server_e2e.py` | Integration (E2E) | Provides an end-to-end test by starting a live server and interacting with its streaming endpoints. |

## Running Tests

- We can run backend tests with:
  ```bash
  make test # unit tests only
  make test-all # all tests
  ```
- We can run frontend tests with:
  ```bash
  cd src/nextjs_fe
  npm test
  ```
- **CI Environment Variable:** Setting `CI=true` is recommended when running tests in a CI/CD pipeline or as a non-interactive agent. It ensures that test runners (like `pytest` or `jest`) run in a single-execution mode rather than a "watch" or "interactive" mode, and it can also be used to suppress interactive prompts or local-only configurations.
- Note that integration tests will fail if the development environment has not first been configured with the `setup-env.sh` script. This is because the test code will not have access to the required Google APIs.

### Testing with Verbose Output

- If we want to run tests verbosely, we can do this:

  ```bash
  uv run pytest -v -s src/tests/unit/test_config.py
  uv run pytest -v -s src/tests/unit/test_personality.py
  uv run pytest -v -s src/tests/integration/test_rickbot_agent_multiturn.py
  uv run pytest -v -s src/tests/integration/test_server_e2e.py
  uv run pytest -v -s src/tests/integration/test_personalities.py
  ```

### Manual Tests for the API

The following `curl` commands can be used to manually test the API endpoints.

#### Single Turn Text-Only Conversation

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=What is the meaning of life?" \
  -F "personality=Rick" \
  -F "user_id=test_user"
```
#### Single Turn Image Conversation

```bash
curl -X POST "http://localhost:8000/chat" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "prompt=Describe this image for me" \
    -F "personality=Jack" \
    -F "user_id=test_user_vision" \
    -F "file=@/home/darren/localdev/python/rickbot-adk/media/get_schwifty_with_fastapi.png" | jq .
```

#### Multi-Turn Conversation

```bash
# First turn
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=My name is Dazbo." \
  -F "personality=Rick" \
  -F "user_id=test_user" \
  -F "session_id=multiturn_test_session"

# Second turn
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=What is my name?" \
  -F "personality=Rick" \
  -F "user_id=test_user" \
  -F "session_id=multiturn_test_session"
```