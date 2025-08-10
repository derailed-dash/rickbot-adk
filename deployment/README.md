# Deployment

This directory contains the Terraform configurations for provisioning the necessary Google Cloud infrastructure for your agent.

The recommended way to deploy the infrastructure and set up the CI/CD pipeline is by using the `agent-starter-pack setup-cicd` command from the root of your project.

However, for a more hands-on approach, you can always apply the Terraform configurations manually for a do-it-yourself setup.

For detailed information on the deployment process, infrastructure, and CI/CD pipelines, please refer to the official documentation:

**[Agent Starter Pack Deployment Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**

## Deployment Overview

### CI Pipeline

E.g. `.github/workflows/pr_checks.yaml` or `.cloudbuild/pr_checks.yaml`

- Triggered on pull request creation/update.
- Runs unit and integration tests to ensure code quality.

### Staging CD Pipeline 

E.g. `.github/workflows/staging.yaml` or `.cloudbuild/staging.yaml`

- Triggered on merge to the main branch.
- Builds and pushes the application container to Artifact Registry.
- Deploys the new version to the staging environment.
- Performs automated load testing against the staging environment.

### Production Deployment

E.g. `.github/workflows/deploy-to-prod.yaml` or `.cloudbuild/deploy-to-prod.yaml`

- Triggered after a successful staging deployment.
- Requires manual approval before proceeding to production.
- Deploys the same container image that was tested in staging to the production environment.

## Development Environment Deployment

Intended for a standalone dev environment without setting up the full CI/CD pipeline. Only use if you're not using the CI/CD pipeline.

- Configuration is in `deployment/terraform/dev`
- We can run using `make setup-dev-env`
