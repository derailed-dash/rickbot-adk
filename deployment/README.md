# Deployment

This directory contains the Terraform configurations for provisioning the necessary Google Cloud infrastructure for your agent.

It was originally created and deployed using the `agent-starter-pack setup-cicd` command from the root of the project. For detailed information on the deployment process, infrastructure, and CI/CD pipelines, please refer to the official documentation:

**[Agent Starter Pack Deployment Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**

Subsequent deployment runs can easily be invoked using `make terraform` from the project root.

## Deployment Overview

### Variables

Variables are configured in `vars/env.tfvars`.

### CI Pipeline

Defined in `.cloudbuild/pr_checks.yaml`

- Triggered on pull request creation/update.
- Runs unit and integration tests to ensure code quality.

### Staging CD Pipeline 

Defined in `.cloudbuild/staging.yaml`

- Triggered on merge to the main branch.
- Builds and pushes the application container to Artifact Registry.
- Deploys the new version to the staging environment.
- Performs automated load testing against the staging environment.

### Production Deployment

Defined in `.cloudbuild/deploy-to-prod.yaml`

- Triggered after a successful staging deployment.
- Requires manual approval before proceeding to production.
- Deploys the same container image that was tested in staging to the production environment.

