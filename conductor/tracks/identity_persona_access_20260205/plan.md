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
- [x] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure and Data Modeling' (Protocol in workflow.md) [checkpoint: e9c5a7d]

## Phase 2: Backend Access Enforcement
- [x] Task: Implement Access Control Middleware in FastAPI. 492f420
    - [x] Write failing tests for middleware (unauthorised access to restricted persona). 492f420
    - [x] Implement `PersonaAccessMiddleware` in `src/rickbot_agent/auth_middleware.py`. 492f420
    - [x] Integrate middleware into the FastAPI app. 492f420
- [x] Task: Refine "Upgrade Required" Response. 4bd29d9
    - [x] Write tests for the specific "Upgrade Required" error response structure. 4bd29d9
    - [x] Implement a custom exception and handler for persona access denial. 4bd29d9
- [x] Task: Conductor - User Manual Verification 'Phase 2: Backend Access Enforcement' (Protocol in workflow.md) [checkpoint: 0d9193f]

## Phase 3: Frontend Integration and Verification
- [x] Task: Handle "Upgrade Required" in the frontend. d3222d6
    - [x] Update frontend API client to recognise the upgrade response.
    - [x] Implement a basic "Access Restricted" modal/message in the UI.
    - [x] Fix Mock Login to support variable user IDs for testing. b220002
- [x] Task: Implement User Metadata Sync. 293ea83
    - [x] Automatically create/update user records in Firestore.
    - [x] Use readable document IDs ({id}_{name}).
    - [x] Track last_logged_in for housekeeping.
- [x] Task: End-to-End Verification. 4f24750
    - [x] Verify a 'standard' user cannot access a 'supporter' persona.
    - [x] Verify a 'supporter' user can access all personas.
    - [x] Verify dynamic updates to persona tiers in Firestore are reflected without restart.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Integration and Verification' (Protocol in workflow.md)
