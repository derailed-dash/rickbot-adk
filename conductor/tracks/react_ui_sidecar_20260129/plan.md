# Implementation Plan - Next.js React UI Integration (Sidecar Architecture)

This plan outlines the steps to integrate the Next.js React UI using a Cloud Run Sidecar architecture, providing a configurable deployment toggle between React and Streamlit.

## Phase 1: Containerization & Local Optimization [checkpoint: b4a4846]

- [x] Task: Create optimized Dockerfiles for the Sidecar architecture [f1694d9]
    - [x] Task: Create `Dockerfile.react_fe` for the Next.js frontend
    - [x] Task: Create `Dockerfile.api_sidecar` for the FastAPI backend
    - [x] Task: Update existing `Dockerfile` (Streamlit) to ensure consistency and slimness
- [x] Task: Update Makefile for local container testing [1f83a40]
    - [x] Task: Add `make docker-react` to build and run the sidecar setup locally using `docker-compose` or similar
    - [x] Task: Update `make docker-streamlit` to use the updated Dockerfile
- [x] Task: Conductor - User Manual Verification 'Phase 1: Containerization' (Protocol in workflow.md)

## Phase 2: Infrastructure as Code (Terraform) [checkpoint: 83c1e1b]

- [x] Task: Update Terraform variables and locals [83c1e1b]
    - [x] Task: Add `ui_type` variable to `variables.tf` (default: "react")
    - [x] Task: Update `locals.tf` to handle conditional logic for container configurations
- [x] Task: Update Cloud Run service definition for Sidecars [83c1e1b]
    - [x] Task: Modify `service.tf` to support multi-container deployments when `ui_type` is "react"
    - [x] Task: Configure `ingress` container (Next.js) and `sidecar` container (FastAPI)
    - [x] Task: Ensure environment variables and secrets are correctly mapped to both containers
- [x] Task: Conductor - User Manual Verification 'Phase 2: Infrastructure' (Protocol in workflow.md)

## Phase 3: CI/CD Pipeline Integration [checkpoint: 721bec9]

- [x] Task: Update Cloud Build configurations [721bec9]
    - [x] Task: Modify `staging.yaml` and `deploy-to-prod.yaml` to conditionally build images based on `ui_type`
    - [x] Task: Implement tagging with Git short SHA for all built images
    - [x] Task: Update deployment step to handle the multi-container service configuration
- [x] Task: Update Pull Request checks [e68dacd]
    - [x] Task: Ensure `pr_checks.yaml` runs relevant tests for both the backend and the React frontend
- [x] Task: Conductor - User Manual Verification 'Phase 3: CI/CD' (Protocol in workflow.md)

## Phase 4: Documentation & Final Verification

- [~] Task: Update Project Documentation
    - [~] Task: Update `README.md` with Local Development guide for Sidecar setup
    - [~] Task: Update `deployment/README.md` with instructions for the `ui_type` toggle
    - [~] Task: Update `docs/design.md` with architecture diagrams for both UI modes
- [ ] Task: Final System Integration Test
    - [ ] Task: Deploy to Staging with `ui_type="react"` and verify end-to-end functionality
    - [ ] Task: Deploy to Staging with `ui_type="streamlit"` and verify fallback functionality
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Documentation & Final Verification' (Protocol in workflow.md)
