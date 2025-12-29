# Unified Testing Documentation

This document serves as the comprehensive guide for testing strategy, execution, and manual verification for the Rickbot-ADK project.

## Table of Contents
0. [General Testing Principles](#general-testing-principles)
   - [CI-Aware Execution](#ci-aware-execution)
   - [Running Tests (All Commands)](#running-tests-all-commands)
1. [Backend Testing Strategy](#backend-testing-strategy)
   - [Test Summary](#test-summary)
   - [Configuration & Test Mode](#configuration--test-mode)
2. [Frontend Testing Strategy](#frontend-testing-strategy)
   - [Stack Overview](#stack-overview)
   - [Writing Frontend Tests](#writing-frontend-tests)
3. [Authentication & Session Management](#authentication--session-management)
   - [Retrieving Bearer Tokens](#retrieving-bearer-tokens)
   - [Mock Tokens](#mock-tokens)
4. [Manual API Verification](#manual-api-verification)
   - [Using Curl with Authentication](#using-curl-with-authentication)
   - [Artifact Retrieval](#artifact-retrieval)

---

## General Testing Principles

Regardless of the component being tested (Backend or Frontend), the following principles apply:

### CI-Aware Execution

All test runners should be aware of the `CI` environment variable. When `CI=true`:
- Test runners must execute once and exit (no watch mode).
- Interactive prompts must be suppressed.
- Output should be optimized for logs.

### Running Tests (All Commands)

#### Backend (Python)
- Run unit tests: `make test`
- Run all tests (Unit + Integration): `make test-all`
- Run specific test file: `uv run pytest -v -s src/tests/unit/test_config.py`

#### Frontend (React/Next.js)
- Run all tests: `cd src/nextjs_fe && npm test`
- Run in watch mode: `cd src/nextjs_fe && npm run test:watch`

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

---

## Frontend Testing Strategy

The Rickbot-ADK frontend is built with Next.js and is tested using a modern React testing stack.

### Stack Overview

- **Jest**: The primary test runner and assertion library.
- **React Testing Library (RTL)**: Used for rendering components and interacting with them in a way that mimics user behavior.
- **jest-environment-jsdom**: Provides a browser-like environment for testing React components.
- **next/jest**: Official Next.js integration for Jest, which automatically configures transform and environment settings.

### Writing Frontend Tests

Frontend tests are located in `src/nextjs_fe/__tests__/`. We follow these conventions:

- **Component Tests**: Focused on individual UI components (e.g., `AuthButton.test.tsx`).
- **Page Tests**: Focused on full pages and their accessibility (e.g., `Privacy.test.tsx`).
- **User-Centric Testing**: Prefer testing behavior (what the user sees and does) over implementation details (internal state or props).

---

## Authentication & Session Management
*(Pending implementation)*

## Manual API Verification
*(Pending implementation)*