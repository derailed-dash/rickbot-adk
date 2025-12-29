# Specification - Unified Testing Documentation

## Overview
Consolidate and expand the project's testing documentation into a single, comprehensive guide. This track involves migrating existing Python-centric testing documentation, adding details for React/Next.js frontend testing, and providing actionable guides for manual API verification using authenticated sessions.

## Functional Requirements
1.  **Documentation Migration**:
    *   Create `docs/testing.md` as the primary testing resource.
    *   Migrate all content from `src/tests/README.md` to `docs/testing.md`.
    *   Archive `src/tests/README.md` once migration is complete.
2.  **Frontend Testing Documentation**:
    *   Explain the React/Next.js testing stack (Jest, React Testing Library).
    *   Describe how to run frontend tests.
    *   Provide guidance on writing new frontend tests (component vs. page tests).
3.  **Authentication & Session Documentation**:
    *   Provide a step-by-step guide for retrieving a Bearer token from the browser (Developer Tools).
    *   (Optional/Helper) Provide a method or script reference for obtaining a mock token for local development.
4.  **Manual Verification Guide**:
    *   Provide `curl` command templates using an `$AUTH_TOKEN` environment variable.
    *   Include specific examples for retrieving ADK Artifacts via the `/artifacts` endpoint using a bearer token.

## Non-Functional Requirements
*   **Clarity**: Documentation must be accessible to developers who haven't worked with React or Next.js before.
*   **Consistency**: Use standard project formatting and terminology.

## Acceptance Criteria
*   `docs/testing.md` exists and is comprehensive.
*   `src/tests/README.md` has been archived/removed.
*   Documentation includes clear instructions for:
    *   Running backend tests (Pytest).
    *   Running frontend tests (Jest).
    *   Retrieving a bearer token.
    *   Using `curl` with the bearer token for artifact retrieval.

## Out of Scope
*   Writing new test cases or improving test coverage.
*   Modifying the authentication logic or security implementation.
