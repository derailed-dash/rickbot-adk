# Specification: User Authentication & API Security

## Context
The application currently allows unauthenticated access to the backend API and frontend. To secure the application and enable personalized experiences, we need to implement user authentication.

## Goals
1.  **Frontend Authentication:**
    -   Implement Google OAuth sign-in in the Next.js frontend.
    -   Implement GitHub OAuth sign-in in the Next.js frontend.
    -   Implement a mechanism to allow mock user in local dev (similar to existing Streamlit approach)
    -   Ensure the user session is maintained securely.
2.  **API Security:**
    -   Secure all backend API endpoints to require a valid authentication token.
    -   Verify tokens passed from the frontend (likely JWTs).
    -   Reject unauthenticated requests with appropriate HTTP error codes (401/403).

## Technical Requirements
-   **Frontend:** Next.js (using NextAuth.js or similar library recommended for OAuth).
-   **Backend:** FastAPI (using `fastapi-users` or custom dependency injection for token verification).
-   **Identity Providers:** Google, GitHub.
-   **Token Standard:** JWT (JSON Web Tokens).

## Out of Scope
-   User role management (RBAC) is out of scope for this initial track.
-   Database storage of user profiles beyond basic auth data needed for the session.
