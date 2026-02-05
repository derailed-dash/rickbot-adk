# Specification: Identity-Based Persona Access Control

## Overview
This track implements an identity-based access control system to restrict persona availability based on the logged-in user's role. It introduces a Role-Based Access Control (RBAC) mechanism using Google Firestore as the source of truth for user roles and persona access requirements. This foundation is designed to support future monetisation through one-time purchase roles.

## Functional Requirements
- **Role-Based Access Control (RBAC):** Implementation of roles (e.g., 'standard', 'supporter') to govern persona access.
- **One-Time Purchase Model:** The role mapping must support a model where users can be granted permanent roles (e.g., via a one-time purchase).
- **Firestore Integration:** 
    - Store user-to-role mappings in a `users` collection.
    - Store persona-to-required-role mappings in a `persona_tiers` (or similar) collection to allow dynamic updates.
- **FastAPI Middleware Enforcement:** Access checks must be enforced at the API middleware level before requests reach the core agent logic.
- **Graceful Upsell Response:** When access is denied, the API must return a structured response (e.g., a specific error code or metadata) that the frontend can use to trigger a "purchase/upgrade" UI flow rather than a generic error.

## Non-Functional Requirements
- **Security:** Ensure user identity (via existing OAuth/JWT) is securely linked to Firestore records.
- **Performance:** Minimise latency added by the Firestore lookup during the request lifecycle (consider caching if necessary).
- **Scalability:** The Firestore schema should be flexible enough to accommodate more roles or complex access rules in the future.

## Acceptance Criteria
- [ ] A user with the 'standard' role cannot initiate a session with a 'supporter'-tier persona.
- [ ] A user with the 'supporter' role can access both 'standard' and 'supporter' personas.
- [ ] The API returns a specific "upgrade required" response when access is denied.
- [ ] Persona-to-role mappings can be updated in Firestore and take effect without a service restart.
- [ ] Unit tests verify the middleware enforcement logic with mocked Firestore responses.

## Out of Scope
- Implementation of the actual payment processing or checkout UI.
- Subscription-based (time-limited) access (deferred to a future track).
- Complex Attribute-Based Access Control (ABAC).
