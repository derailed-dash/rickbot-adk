# Rickbot-ADK

## Repo Metadata

Author: Darren Lester

## Repo Overview

_Rickbot_ is a multi-personality chatbot built using Google Gemini, the Agent Development Kit (ADK), Gemini CLI, and the Google Agent-Starter-Pack. It has many personalities, such as Rick Sanchez (Rick and Morty), Yoda, The Donald, Jack Burton (Big Trouble in Little China), and Dazbot.

The original _Rickbot_ repo is [here](https://github.com/derailed-dash/rickbot). The intent with this repo is to demonstrate leveraging some additional tools in order to evolve the first _Rickbot_ iteration. In particular:

- Updating the original Rickbot to make use of the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Creating the initial project folder, GitHub repo and CI/CD using the [Agent-Starter-Pack](https://googlecloudplatform.github.io/agent-starter-pack/).
- Adding new capabilities to Rickbot.
- Using [Gemini CLI](https://medium.com/google-cloud/give-gemini-cli-the-ability-to-generate-images-and-video-work-with-github-repos-and-use-other-482172571f99) to help with the overall migration journey.

## Table of Contents

- [Associated Articles](#associated-articles)
- [Per Dev Session (Once One-Time Setup Tasks Have Been Completed)](#per-dev-session-once-one-time-setup-tasks-have-been-completed)
- [For Local Dev and Testing](#for-local-dev-and-testing)
  - [ADK](#adk)
- [Make Commands](#make-commands)
- [Using Agent Starter Kit for Initial Project Setup](#using-agent-starter-kit-for-initial-project-setup)
  - [Pre-Reqs](#pre-reqs)
  - [Before Creating Project with Agent Starter Kit](#before-creating-project-with-agent-starter-kit)
  - [Create Project with Agent Starter Kit](#create-project-with-agent-starter-kit)
  - [After Creating Project with Agent Starter Kit](#after-creating-project-with-agent-starter-kit)
  - [Creating CI/CD Pipeline](#creating-ci-cd-pipeline)
- [Deploying Infra Commands](#deploying-infra-commands)

## Associated Articles

See my Medium articles which are intended to supplement this repo:

1. [Enhancing the Rickbot Multi-Personality Agentic Application - using Gemini CLI, Google Agent-Starter-Pack and the Agent Development Kit (ADK)](https://medium.com/google-cloud/building-the-rickbot-multi-personality-agentic-application-using-gemini-cli-google-a48aed4bef24)
1. Updating the Rickbot Multi-Personality Agentic Application - Integrate Agent Development Kit (ADK) using Gemini CLI

## Per Dev Session (Once One-Time Setup Tasks Have Been Completed)

```bash
# From rickbot-adk project folder
source .env

gcloud auth login --update-adc
export STAGING_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_STAGING_PROJECT --format="value(projectNumber)")
export PROD_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PRD_PROJECT --format="value(projectNumber)")
export GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_STAGING_PROJECT

gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config list project

uv sync --dev --extra jupyter # Or we can use make install, from Agent Starter Kit
source .venv/bin/activate
```

## For Local Dev and Testing

Install required packages and launch the local development environment:

```bash
make install && make playground
```

### ADK

#### Testing Locally

With CLI:

```bash
uv run adk run rickbot_agent
```

With GUI:

```bash
uv run adk web

# Or we can use the Agent Starter Git make aliases
make install && make playground
```

#### Testing Remote

Use the `adk_app_testing.ipynb` notebook.

## Make Commands

| Command | Description |
| ------- | ----------- |
| `make install`       | Install all required dependencies using uv |
| `make playground`    | Launch Streamlit interface for testing agent locally and remotely |
| `make backend`       | Deploy agent to Agent Engine |
| `make test`          | Run unit and integration tests |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)  |
| `make setup-dev-env` | Set up development environment resources using Terraform   |
| `uv run jupyter lab` | Launch Jupyter notebook  |

For full command options and usage, refer to the [Makefile](Makefile).

## Using Agent Starter Kit for Initial Project Setup

### Pre-Reqs

- Dev and Prod GCP projects created and attached to a billing account and your user is the owner of both projects.
- GitHub CLI (gh) installed and authenticated
- uv (Python package manager) installed
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk) installed
- Terraform installed

### Before Creating Project with Agent Starter Kit

```bash
# Authenticate and update ADC
# Your user needs to be the owner of both projects
gcloud auth login --update-adc

export GOOGLE_CLOUD_STAGING_PROJECT="your-dev-project"
export GOOGLE_CLOUD_PRD_PROJECT="your-prod-project"

# Make sure we're on the Dev / Staging project...
export GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_STAGING_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config list project

# Now let's enable some Google Cloud APIs in the project
gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  storage-component.googleapis.com \
  aiplatform.googleapis.com
```

### Create Project with Agent Starter Kit

```bash
# Dependency is Python and uv already installed
uvx agent-starter-pack create rickbot-adk
```

Let's use:

- `adk_base` as our ADK template application.
- Google Vertex AI Agent Engine as our agent hosting service
- Google Cloud Build for our CI/CD pipeline

After running, we now have:

```text
rickbot-adk/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── agent_engine_app.py
│   └── utils/
│       ├── gcs.py
│       ├── tracing.py
│       └── typing.py
|
├── deployment/
│   ├── README.md
│   └── terraform/
│       ├── dev/
│       ├── vars/
│       ├── apis.tf
│       ├── build_triggers.tf
│       ├── github.tf
│       ├── iam.tf
│       ├── locals.tf
│       ├── log_sinks.tf
│       ├── providers.tf
│       ├── service_accounts.tf
│       ├── storage.tf
│       └── variables.tf
│
├── notebooks/
│   ├── adk_app_testing.ipynb
│   ├── evaluating_adk_agent.ipynb
│   └── intro_agent_engine.ipynb
|
├── tests/
│   ├── integration/
│   │   ├── test_agent.py
│   │   └── test_agent_engine_app.py
│   ├── load_test/
│   │   ├── README.md
│   │   └── load_test.py
│   └── unit/
│       └── test_dummy.py
|
├── GEMINI.md
├── Makefile
├── pyproject.toml
├── README.md
└── uv.lock
```

### After Creating Project with Agent Starter Kit

- Update `pyproject.toml`.
- Create `.env`.
- Update `README.md` (this file)

### Creating CI/CD Pipeline

First, one-time setup for Prod project. (To workaround issues I found with the `setup-cicd` command.)

```bash
# Make sure we're on the Prod/CICD project...
export GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PRD_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config list project

gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PRD_PROJECT \
    --member="serviceAccount:service-$PROD_PROJECT_NUMBER@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"
```

Now we can run `setup-cicd`:

```bash
uvx agent-starter-pack setup-cicd \
  --staging-project $GOOGLE_CLOUD_STAGING_PROJECT \
  --prod-project $GOOGLE_CLOUD_PRD_PROJECT \
  --repository-name $REPO \
  --region $GOOGLE_CLOUD_BUILD_REGION # I have no quota to run Cloud Build in my preferred region
```

The following is just for my own quota issue. May not apply to others! Update the following to split out REGION and CB_REGION:

- staging.yaml
- build_triggers.tf
- github.tf
- variables.tf
- env.tfvars (x2)

## Deploying Infra Commands

If we need to redeploy...

```bash
# Assuming we're in the project root folder
cd deployment/terraform
terraform init # One time initialisation

# Create the TF plan
terraform plan -var-file="vars/env.tfvars" -out out.tfplan

# Check the TF plan then apply
terraform apply "out.tfplan"
```
