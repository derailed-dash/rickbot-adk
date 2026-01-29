# Track Specification: Next.js React UI Integration (Sidecar Architecture)

## 1. Overview
This track introduces a modern React-based frontend (Next.js) to the Rickbot-ADK project using a Cloud Run Sidecar architecture. It allows for a single deployment unit (one Cloud Run service) to host both the optimized Node.js frontend and the Python FastAPI backend, while maintaining a fallback option for the existing Streamlit UI.

## 2. Functional Requirements
1.  **Dual UI Support:** The system must support two distinct user interfaces:
    *   **React UI:** A Next.js application (located in `src/nextjs_fe`).
    *   **Streamlit UI:** The legacy Python-based interface (located in `src/streamlit_fe`).
2.  **Configurable Deployment:** Use a Terraform variable (`ui_type`) to toggle the deployment mode.
    *   `ui_type = "react"`: Deploys the Next.js Ingress container and FastAPI Sidecar container.
    *   `ui_type = "streamlit"`: Deploys the single-container Streamlit application (legacy mode).
3.  **Local Communication:** In the React deployment, the Next.js frontend must communicate with the FastAPI backend via `http://localhost:[PORT]`.
4.  **Optimized Images:** 
    *   Create a `Dockerfile.react_fe` for the Next.js application.
    *   Create a `Dockerfile.api_sidecar` for the FastAPI/Agent backend.
    *   Retain/Update the existing `Dockerfile` for Streamlit.
5.  **Documentation Updates:** 
    *   `README.md`: Add Developer Guide for running the Sidecar setup locally.
    *   `deployment/README.md`: Update deployment guidance, including how to configure the build type.
    *   `docs/design.md`: Document the overall architecture of the two approaches (Streamlit vs. Sidecar).

## 3. Non-Functional Requirements
1.  **Cost Efficiency:** Use a single Cloud Run service to host both containers in the React setup to minimize costs and networking complexity.
2.  **Performance:** Next.js should handle ingress to allow for Server-Side Rendering (SSR) and efficient static asset delivery.
3.  **Security:** Maintain existing OAuth configurations, ensuring tokens are passed correctly between the frontend and backend over the local network.
4.  **Traceability:** Docker images should be tagged with the Git short SHA.

## 4. Acceptance Criteria
- [ ] Successfully build separate Docker images for React FE and API Sidecar, tagged with Git short SHA.
- [ ] Terraform correctly deploys a multi-container service when `ui_type` is "react".
- [ ] Terraform correctly deploys a single-container service when `ui_type` is "streamlit".
- [ ] Next.js UI can successfully call the FastAPI backend and receive agent responses via localhost.
- [ ] Existing domain mappings correctly route traffic to the ingress container.
- [ ] CI/CD pipeline correctly handles conditional builds and deployments based on the selected UI.
- [ ] Documentation (`README.md`, `deployment/README.md`, `docs/design.md`) is updated and accurate.

## 5. Out of Scope
*   Replacing the FastAPI backend logic.
*   Merging the two UI codebases into a single monorepo (they remain in `src/`).
