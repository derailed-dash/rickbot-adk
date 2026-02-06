# Implementation Plan: Identity-Based Persona Access Control

This plan implements a Role-Based Access Control (RBAC) system for restricting persona access using Google Firestore as the source of truth, including the initial infrastructure setup via Terraform.

## Phase 1: Infrastructure and Data Modeling
- [x] Task: Provision Google Firestore via Terraform. 580a001
    - [x] Add Firestore database resource to `deployment/terraform/storage.tf` (or a new `firestore.tf`). 580a001
    - [x] Update `deployment/terraform/variables.tf` to include necessary Firestore roles (e.g., `roles/datastore.user`) in `app_sa_roles`. 580a001
    - [x] Ensure the necessary APIs and IAM permissions are configured in `apis.tf` and `iam.tf`. 580a001
    - [x] Apply Terraform changes to the development environment. 580a001
- [x] Task: Set up Firestore collections and seeding. 467a99d
    - [x] Define `users` collection schema with `role` field. 467a99d
    - [x] Define `persona_tiers` collection schema mapping `persona_id` to `required_role`. 467a99d
    - [x] Seed Firestore with initial data for testing (e.g., standard vs. supporter personas). 467a99d
- [x] Task: Implement Firestore service utility in the backend. 572e6b3
    - [x] Write tests for Firestore role and tier retrieval. 572e6b3
    - [x] Implement `get_user_role(user_id)` in `src/rickbot_agent/services.py`. 572e6b3
    - [x] Implement `get_required_role(persona_id)` in `src/rickbot_agent/services.py`. 572e6b3
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure and Data Modeling' (Protocol in workflow.md)

## Phase 2: Backend Access Enforcement
- [ ] Task: Implement Access Control Middleware in FastAPI.
    - [ ] Write failing tests for middleware (unauthorised access to restricted persona).
    - [ ] Implement `PersonaAccessMiddleware` in `src/rickbot_agent/auth_middleware.py`.
    - [ ] Integrate middleware into the FastAPI app.
- [ ] Task: Refine "Upgrade Required" Response.
    - [ ] Write tests for the specific "Upgrade Required" error response structure.
    - [ ] Implement a custom exception and handler for persona access denial.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backend Access Enforcement' (Protocol in workflow.md)

## Phase 3: Frontend Integration and Verification
- [ ] Task: Handle "Upgrade Required" in the frontend.
    - [ ] Update frontend API client to recognise the upgrade response.
    - [ ] Implement a basic "Access Restricted" modal/message in the UI.
- [ ] Task: End-to-End Verification.
    - [ ] Verify a 'standard' user cannot access a 'supporter' persona.
    - [ ] Verify a 'supporter' user can access all personas.
    - [ ] Verify dynamic updates to persona tiers in Firestore are reflected without restart.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Integration and Verification' (Protocol in workflow.md)
