# Deployment

This directory contains the Terraform configurations for provisioning the necessary Google Cloud infrastructure for your agent.

It was originally created and deployed using the `agent-starter-pack setup-cicd` command from the root of the project. For detailed information on the deployment process, infrastructure, and CI/CD pipelines, please refer to the official documentation:

**[Agent Starter Pack Deployment Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**

Subsequent deployment runs can easily be invoked using `make terraform` from the project root.

## Deployment Overview

### Unified Container Architecture

The application is deployed as a single, unified container based on `Dockerfile.unified`. This image incorporates:
*   **React Frontend**: Built using Next.js (Node.js v20), served statically or via SSR.
*   **FastAPI Backend**: Serving the agent API and ADK-powered chat functionalities.
*   **Reverse Proxy**: The container manages routing between the UI and API layers.

### Data & Persistence

The application uses several Google Cloud services for data storage and state management:
*   **Google Cloud Storage (GCS)**: Used for storing user-uploaded artifacts and session logs.
*   **Google Firestore**: Serves as the source of truth for Role-Based Access Control (RBAC). It stores user roles and persona access requirements. 
    *   **PITR**: Point-in-Time Recovery is enabled, providing 7 days of data retention.
    *   **Rationale**: See the [Storage Strategy (docs/design.md)](../docs/design.md#6-storage-strategy-firestore-vs-cloud-sql) for why we chose Firestore over Cloud SQL.

#### Seeding Firestore

For development and initial setup, a seeding script is provided to populate Firestore with default roles and tiers:

```bash
uv run python scripts/seed_firestore.py
```

### Mandatory Environment Variables and Secrets

The following configurations are required for the application to function, particularly for authentication. 

#### OAuth Setup & Secret Management

Rickbot uses OAuth for securing the application. You must configure OAuth credentials for both Google and GitHub providers. It is recommended to create separate OAuth applications for Development (Dev) and Production (Prod) environments.

| Variable/Secret | Type | Source (Dev) | Source (Prod - Secret Manager) |
| :--- | :--- | :--- | :--- |
| `NEXTAUTH_SECRET` | Secret | Random string in `.env.local` | `rickbot-nextauth-secret` |
| `GOOGLE_CLIENT_ID` | Variable | [GCP Console](https://console.cloud.google.com/apis/credentials) | [GCP Console](https://console.cloud.google.com/apis/credentials) |
| `GOOGLE_CLIENT_SECRET` | Secret | [GCP Console](https://console.cloud.google.com/apis/credentials) | `rickbot-google-client-secret` |
| `GITHUB_CLIENT_ID` | Variable | [GitHub Settings](https://github.com/settings/developers) | [GitHub Settings](https://github.com/settings/developers) |
| `GITHUB_CLIENT_SECRET` | Secret | [GitHub Settings](https://github.com/settings/developers) | `rickbot-github-client-secret` |
| `NEXTAUTH_URL` | Variable | `http://localhost:3000` | Automated via Terraform |

#### Google Cloud Secret Manager (Production)

For production deployment, avoid embedding secrets in the container image. Instead, mount secrets from **Google Secret Manager** directly as environment variables:

1.  **Create Secrets**: Store `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_SECRET`, and `GITHUB_CLIENT_SECRET` in Secret Manager.
2.  **Mount Secrets**: Configure the Cloud Run service (via Terraform or Console) to mount these:
    *   `NEXTAUTH_SECRET` -> `projects/PROJECT_ID/secrets/rickbot-nextauth-secret/versions/latest`

#### Environment Configuration Files

The project maintain separation between Backend and Frontend configurations during development.

##### 1. Backend: Root Directory `.env`
Configures the FastAPI server. Loaded via `source scripts/setup-env.sh`.

| Variable | Purpose |
| :--- | :--- |
| `GOOGLE_CLIENT_ID` | Verifies Google ID Tokens sent by the frontend. |
| `BACKEND_ALLOW_MOCK_AUTH` | Enables bypass of real OAuth for local role testing. **Keep out of prod.** |
| `GOOGLE_CLOUD_PROJECT` | Used for ADK and Secret Manager access. |

##### 2. Frontend: `src/nextjs_fe/.env.local`
Exclusively used by the Next.js application.

| Variable | Purpose |
| :--- | :--- |
| `NEXT_PUBLIC_ALLOW_MOCK_AUTH` | Enables the "Mock Login" provider in the UI. |
| `NEXT_PUBLIC_API_URL` | URL of the backend API (e.g., `http://localhost:8000`). |
| `MOCK_AUTH_USER` | Email address assigned to the mock user identity. |

#### `NEXTAUTH_URL` Management
In the continuous deployment pipeline, `NEXTAUTH_URL` is automatically derived by Terraform from the `staging_app_domain_name` or `prod_app_domain_name` variables and passed as a Cloud Build substitution.

### Environment Management: Staging and Production

This project utilizes distinct Google Cloud Projects to manage **staging** and **production** environments. This separation ensures isolation and allows for independent testing and deployment workflows.

*   **Project IDs:** The specific Google Cloud Project IDs for these environments are defined as variables in `deployment/terraform/variables.tf` (e.g., `prod_project_id`, `staging_project_id`).
*   **Variable Assignment:** The actual values for these project IDs are assigned in `deployment/terraform/vars/env.tfvars`.
*   **Environment Grouping:** The `deployment/terraform/locals.tf` file groups these project IDs into a `deploy_project_ids` map, which facilitates iteration and consistent application of configurations across environments within Terraform.

### Variable Definition and Usage

*   **Definition (`deployment/terraform/variables.tf`):** This file declares all input variables for the Terraform configuration.
*   **Assignment (`deployment/terraform/vars/env.tfvars`):** This file is used to assign concrete values to the variables declared in `variables.tf`. This allows for environment-specific configurations.
    *   **GitHub Variables**: The variables `github_app_installation_id` and `github_pat_secret_id` are crucial for the Cloud Build repository connection.
        *   `github_app_installation_id`: Obtained from the GitHub App installation URL settings on your repository.
        *   `github_pat_secret_id`: The ID of a secret in Google Secret Manager that holds your GitHub Personal Access Token (PAT). This PAT is required for Terraform to authenticate with GitHub.
        *   `host_connection_name`: The name required for the Cloud Build host connection resource.

### CI/CD Pipeline Creation

The entire CI/CD pipeline for this project was initially set up using the `uvx agent-starter-pack setup-cicd` command. This command automates several critical steps:

1.  **GitHub Repository Creation:** It can create a new GitHub repository for your project.
2.  **CI/CD Runner Connection:** It connects your GitHub repository to your chosen CI/CD runner (e.g., Google Cloud Build or GitHub Actions).
3.  **Infrastructure Provisioning:** It provisions the necessary staging and production infrastructure in your Google Cloud projects.
4.  **Deployment Triggers:** It configures deployment triggers based on your repository's activity (e.g., pull requests, merges to `main`).

It has since been modified extensively.

### Cloud Build Integration

This project leverages Google Cloud Build for its CI/CD workflows. The build configurations are defined in the `.cloudbuild/` directory:

*   **`pr_checks.yaml` (CI Pipeline):**
    *   **Trigger:** Activated on pull request creation or updates.
    *   **Purpose:** Ensures code quality and functionality before merging.
    *   **Steps:**
        *   Installs Python dependencies using `uv`.
        *   Runs unit tests (`pytest src/tests/unit`).
        *   Runs integration tests (`pytest src/tests/integration`).
*   **`staging.yaml` (Staging CD Pipeline):**
    *   **Trigger:** Activated on merges to the `main` branch.
    *   **Purpose:** Builds, tests, and deploys the application to the staging environment.
    *   **Steps:**
        *   **Build:** Builds the Docker image of the application and tags it with the `SHORT_SHA` (commit SHA).
        *   **Push:** Pushes the built Docker image to Artifact Registry.
        *   **Deploy to Staging:** Deploys the image to a Cloud Run service in the staging project. Environment variables (e.g., `GOOGLE_CLOUD_PROJECT`, `LOG_LEVEL`, `MODEL`) are passed via `--set-env-vars`.
        *   **Trigger Prod Deployment:** After a successful staging deployment, it triggers the production deployment Cloud Build job.
    *   **Substitutions:** Uses Cloud Build substitutions (e.g., `_STAGING_PROJECT_ID`, `_REGION`, `_SERVICE_NAME`) to dynamically configure the build and deployment based on environment-specific values.
*   **`deploy-to-prod.yaml` (Production Deployment):**
    *   **Trigger:** Manually triggered after a successful staging deployment (often with a manual approval step in Cloud Build).
    *   **Purpose:** Deploys the *same* container image that was tested in staging to the production environment.
    *   **Steps:**
        *   Deploys the pre-built and tested image to a Cloud Run service in the production project.
    *   **Substitutions:** Similar to staging, it uses substitutions (e.g., `_PROD_PROJECT_ID`, `_SERVICE_NAME`) to ensure the correct production environment is targeted.
    *   **Precedence Note**: The variables defined in the `substitutions` block of the YAML files act as **defaults**. They are overridden by substitutions defined in the Cloud Build Trigger itself (which are configured via Terraform). This allows the same YAML file to be reused across different environments or configurations by simply changing the trigger definitions.

### Iteration and Environment Specifics in CI/CD

The CI/CD pipelines are designed to handle multiple environments through:

*   **Project ID Variables:** Cloud Build substitutions like `_STAGING_PROJECT_ID` and `_PROD_PROJECT_ID` are used in the `.cloudbuild` YAML files to ensure that deployments target the correct Google Cloud Project based on the environment.
*   **Shared Image:** The same Docker image built and tested in the staging pipeline is promoted to production, ensuring consistency and reducing the risk of environment-specific issues.
*   **Environment Variables:** Application configurations (e.g., `LOG_LEVEL`, `MODEL`, `AUTH_REQUIRED`) are passed as environment variables during deployment, allowing for environment-specific tuning.

### Additional Useful Information

*   **Convenience Commands:** The `Makefile` in the project root provides several convenient commands for development and deployment:
    *   `make install`: Installs Python dependencies using `uv`.
    *   `make terraform`: Applies the Terraform configurations.
    *   `make backend`: Builds and deploys the agent to Cloud Run.
    *   `make playground`: Starts a local web UI for interactive agent testing.
