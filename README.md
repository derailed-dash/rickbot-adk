# Rickbot-ADK

<img src="media/rickbot-adk-800w.gif" alt="Rickbot" width="800" />

## Repo Metadata

Author: Darren Lester

## Table of Contents

- [Repo Overview](#repo-overview)
- [Associated Articles](#associated-articles)
- [Per Dev Session (Once One-Time Setup Tasks Have Been Completed)](#per-dev-session-once-one-time-setup-tasks-have-been-completed)
- [Useful Commands](#useful-commands)
  - [Streamlit UI](#streamlit-ui)
  - [ADK](#adk)
    - [Testing Locally](#testing-locally)
    - [Testing Remote](#testing-remote)
  - [Running in a Local Container](#running-in-a-local-container)
- [Using Agent Starter Kit for Initial Project Setup](#using-agent-starter-kit-for-initial-project-setup)
  - [Pre-Reqs](#pre-reqs)
  - [Before Creating Project with Agent Starter Kit](#before-creating-project-with-agent-starter-kit)
  - [Create Project with Agent Starter Kit](#create-project-with-agent-starter-kit)
  - [After Creating Project with Agent Starter Kit](#after-creating-project-with-agent-starter-kit)
  - [Creating CI/CD Pipeline](#creating-ci-cd-pipeline)
- [Deploying Infra Commands](#deploying-infra-commands)

## Repo Overview

_Rickbot_ is a multi-personality chatbot built using Google Gemini, the Agent Development Kit (ADK), Gemini CLI, and the Google Agent-Starter-Pack. It has many personalities, such as Rick Sanchez (Rick and Morty), Yoda, The Donald, Jack Burton (Big Trouble in Little China), and Dazbot.

The original _Rickbot_ repo is [here](https://github.com/derailed-dash/rickbot). The intent with this repo is to demonstrate leveraging some additional tools in order to evolve the first _Rickbot_ iteration. In particular:

- Updating the original Rickbot to make use of the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Creating the initial project folder, GitHub repo and CI/CD using the [Agent-Starter-Pack](https://googlecloudplatform.github.io/agent-starter-pack/).
- Adding new capabilities to Rickbot.
- Using [Gemini CLI](https://medium.com/google-cloud/give-gemini-cli-the-ability-to-generate-images-and-video-work-with-github-repos-and-use-other-482172571f99) to help with the overall migration journey.

## Associated Articles

See my Medium articles which are intended to supplement this repo:

1. [Creating a Rick & Morty Chatbot with Google Cloud and the Gen AI SDK](https://medium.com/google-cloud/creating-a-rick-morty-chatbot-with-google-cloud-and-the-gen-ai-sdk-e8108e83dbee)
1. [Adding Authentication and Authorisation to our Rickbot Streamlit Chatbot with OAuth and the Google Auth Platform](https://medium.com/google-cloud/adding-authentication-and-authorisation-to-our-rickbot-streamlit-chatbot-with-oauth-and-the-google-b892cda3f1d9)
1. [Building the Rickbot Multi-Personality Agentic Application using Gemini CLI, Google Agent-Starter-Pack and the Agent Development Kit (ADK)](https://medium.com/google-cloud/building-the-rickbot-multi-personality-agentic-application-using-gemini-cli-google-a48aed4bef24)
1. [Updating the Rickbot Multi-Personality Agentic Application - Integrate Agent Development Kit (ADK) using Gemini CLI](https://medium.com/google-cloud/updating-the-rickbot-multi-personality-agentic-application-part-2-integrate-agent-development-ad39203e66ad)
1. [Guided Implementation of Agent Development Kit (ADK) with the Rickbot Multi-Personality Application (Series)](https://medium.com/google-cloud/updating-the-rickbot-multi-personality-agentic-application-part-3-guided-implementation-of-the-9675d3f92c11)
1. [Productionising the Rickbot ADK Application and More Gemini CLI Tips](https://medium.com/google-cloud/productionising-the-rickbot-adk-application-and-more-gemini-cli-tips-577cf6b37366)

## Per Dev Session (Once One-Time Setup Tasks Have Been Completed)

**DO THIS STEP BEFORE EACH DEV SESSION**

To configure your shell for a development session, **source** the `scripts/setup-env.sh` script. This will handle authentication, set the correct Google Cloud project, install dependencies, and activate the Python virtual environment.

```bash
### Prereqs ###
# If running on WSL, consider first installing wslu

# For the Staging/Dev environment (default)
source scripts/setup-env.sh

# For the Production environment
source scripts/setup-env.sh --target-env PROD

# If authentication is not required
source scripts/setup-env.sh --noauth
```

## Useful Commands

| Command                       | Description                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| `source scripts/setup-env.sh` | Setup Google Cloud project and auth with Dev/Staging. Parameter options:<br> `[--noauth] [-t\|--target-env <DEV\|PROD>]` |
| `make install`                | Install all required dependencies using `uv`                                          |
| `make playground`             | Launch UI for testing agent locally and remotely. This runs `uv run adk web src`      |
| `make streamlit`              | Run Streamlit FE: `MOCK_AUTH_USER="mock.user@example.com" uv run streamlit run src/streamlit_fe/app.py`|
| `make test`                   | Run unit and integration tests                                                        |
| `make lint`                   | Run code quality checks (codespell, ruff, mypy)                                       |
| `make terraform`              | Plan Terraform, prompt for authorisation, then apply                                  |
| `uv run jupyter lab`          | Launch Jupyter notebook                                                               |

For full command options and usage, refer to the [Makefile](Makefile).

### Streamlit UI

```bash
# from src folder
uv run streamlit run src/frontend/streamlit_app.py
```

### Testing

- All tests are in the `src/tests` folder.
- We can run our tests with `make test`.
- Note that integration tests will fail if the development environment has not first been configured with the `setup-env.sh` script. This is because the test code will not have access to the required Google APIs.
- If we want to run tests verbosely, we can do this:

  ```bash
  uv run pytest -v -s src/tests/unit/test_config.py
  uv run pytest -v -s src/tests/unit/test_personality.py
  uv run pytest -v -s src/tests/integration/test_rickbot_agent_multiturn.py
  uv run pytest -v -s src/tests/integration/test_server_e2e.py
  uv run pytest -v -s src/tests/integration/test_personalities.py
  ```

#### Testing Locally

With CLI:

```bash
uv run adk run src/rickbot_agent
```

With GUI:

```bash
# Last param is the location of the agents
uv run adk web src

# Or we can use the Agent Starter Git make aliases
make install && make playground
```

### Running in a Local Container

```bash
# from project root directory

# Get a unique version to tag our image
export VERSION=$(git rev-parse --short HEAD)

# To build as a container image
docker build -t $SERVICE_NAME:$VERSION .

# To run as a local container
# We need to pass environment variables to the container
# and the Google Application Default Credentials (ADC)
docker run --rm -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT -e GOOGLE_CLOUD_REGION=$GOOGLE_CLOUD_REGION \
  -e LOG_LEVEL=$LOG_LEVEL \
  -e APP_NAME=$APP_NAME \
  -e AGENT_NAME=$AGENT_NAME \
  -e GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI \
  -e MODEL=$MODEL \
  -e AUTH_REQUIRED=$AUTH_REQUIRED \
  -e RATE_LIMIT=$RATE_LIMIT \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/.config/gcloud/application_default_credentials.json" \
  --mount type=bind,source=${HOME}/.config/gcloud,target=/app/.config/gcloud \
   $SERVICE_NAME:$VERSION
```

## Using Agent Starter Kit for Initial Project Setup

This project, its GitHub repo, and associated CI/CD pipeline were initially setup using the Agent Starter Kit. Much of the original template files have since been removed from the project.  But this section has been retained to provide an overview of this process. But do read [this article](https://medium.com/google-cloud/building-the-rickbot-multi-personality-agentic-application-using-gemini-cli-google-a48aed4bef24) for a more detailed walkthrough.

## Deploying Infrastructure

The following commands describe how to run Terraform tasks, to deploy infrastructure. Note that I have now added a `terraform` target to my `Makefile`, so we can achieve the same result by simply running `make terraform` from the project root directory.

```bash
# Assuming we're in the project root folder
cd deployment/terraform
terraform init # One time initialisation

# Create the TF plan
terraform plan -var-file="vars/env.tfvars" -out out.tfplan

# Check the TF plan then apply
terraform apply "out.tfplan"
```

## OAuth

Frontend user authentication is required for Rickbot.

### Streamlit

- With the Streamlit frontend this is achieved using Streamlit\'s integrated OIDC authentication. 
- We use Google Auth Platform as the OAuth2 Auth provider.
- OAuth credentials are obtained from the Google Auth Platform and stored in Google Secret Manager.
- When the application is first launched, these credentials are read and dynamically written to the `.streamlit/secrets.toml`, which is how the Streamlit OIDC works. We must supply the `oauth2callback` URI as well as the OAuth client ID and secret.
- Different credentials are used between Staging and Prod.
- When running locally we use an environment variable `MOCK_AUTH_USER` to bypass real authentication. This is automatically set by `make streamlit`.

## DNS

Google Cloud Run offers a native domain name mapping feature. This is used to map custom domains to our Cloud Run services. Note that any custom domains used must be added to the OAuth authorised domains and authorised redirect URIs. 