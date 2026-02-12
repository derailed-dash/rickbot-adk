# Rickbot-ADK

<img src="media/rickbot-adk-800w.gif" alt="Rickbot" width="800" />

## Repo Metadata

Author: Darren Lester

## Table of Contents

- [Repo Overview](#repo-overview)
- [Quick Start: Local Development](#quick-start-local-development)
- [Associated Articles](#associated-articles)
  - [Rickbot Articles](#rickbot-articles)
  - [Related ADK Articles](#related-adk-articles)
- [Developing With This Repo](#developing-with-this-repo)
  - [Per Dev Session (Once One-Time Setup Tasks Have Been Completed)](#per-dev-session-once-one-time-setup-tasks-have-been-completed)
  - [Useful Commands](#useful-commands)
  - [Testing](#testing)
  - [Running ADK Dev Tools](#running-adk-dev-tools)
  - [Running in a Local Container](#running-in-a-local-container)
- [Application Design](docs/design.md)
- [Container Architecture & Local Dev](docs/containers.md)
- [Cloud Infrastructure & Deployment](deployment/README.md)
- [Testing](docs/testing.md)
- [Historical Notes About This Repo](#historical-notes-about-this-repo)
  - [Using Agent Starter Kit for Initial Project Setup](#using-agent-starter-kit-for-initial-project-setup)

## Repo Overview

_Rickbot_ is a multi-personality chatbot built using Google Gemini, the Agent Development Kit (ADK), Gemini CLI, and the Google Agent-Starter-Pack. It has many personalities, such as Rick Sanchez (Rick and Morty), Yoda, The Donald, Jack Burton (Big Trouble in Little China), and Dazbot.

The original _Rickbot_ repo is [here](https://github.com/derailed-dash/rickbot). The intent with this repo is to demonstrate leveraging some additional tools in order to evolve the first _Rickbot_ iteration. In particular:

- Updating the original Rickbot to make use of the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Creating the initial project folder, GitHub repo and CI/CD using the [Agent-Starter-Pack](https://googlecloudplatform.github.io/agent-starter-pack/).
- Adding new capabilities to Rickbot.
- Using [Gemini CLI](https://medium.com/google-cloud/give-gemini-cli-the-ability-to-generate-images-and-video-work-with-github-repos-and-use-other-482172571f99) to help with the overall migration journey.

## Quick Start: Local Development

To get the application running on your local machine, follow these three steps:

1.  **Configure Environment**:
    ```bash
    source scripts/setup-env.sh
    ```
2.  **Start the Backend**:
    In your first terminal:
    ```bash
    make api
    ```
3.  **Start the Frontend**:
    In a second terminal:
    ```bash
    cd src/nextjs_fe && npm install && npm run dev
    ```

For advanced local setup (Docker, Streamlit, etc.), refer to the **[Container & Local Dev Guide](docs/containers.md)**.

## Associated Articles

### Rickbot Articles

See my Medium articles which are intended to supplement this _Rickbot_ repo:

1. [Creating a Rick & Morty Chatbot with Google Cloud and the Gen AI SDK](https://medium.com/google-cloud/creating-a-rick-morty-chatbot-with-google-cloud-and-the-gen-ai-sdk-e8108e83dbee)
1. [Adding Authentication and Authorisation to our Rickbot Streamlit Chatbot with OAuth and the Google Auth Platform](https://medium.com/google-cloud/adding-authentication-and-authorisation-to-our-rickbot-streamlit-chatbot-with-oauth-and-the-google-b892cda3f1d9)
1. [Building the Rickbot Multi-Personality Agentic Application using Gemini CLI, Google Agent-Starter-Pack and the Agent Development Kit (ADK)](https://medium.com/google-cloud/building-the-rickbot-multi-personality-agentic-application-using-gemini-cli-google-a48aed4bef24)
1. [Updating the Rickbot Multi-Personality Agentic Application - Integrate Agent Development Kit (ADK) using Gemini CLI](https://medium.com/google-cloud/updating-the-rickbot-multi-personality-agentic-application-part-2-integrate-agent-development-ad39203e66ad)
1. [Guided Implementation of Agent Development Kit (ADK) with the Rickbot Multi-Personality Application (Series)](https://medium.com/google-cloud/updating-the-rickbot-multi-personality-agentic-application-part-3-guided-implementation-of-the-9675d3f92c11)
1. [Productionising the Rickbot ADK Application and More Gemini CLI Tips](https://medium.com/google-cloud/productionising-the-rickbot-adk-application-and-more-gemini-cli-tips-577cf6b37366)
1. [Get Schwifty with the FastAPI: Adding a REST API to our Agentic Application (with Google ADK)](https://medium.com/google-cloud/get-schwifty-with-the-fastapi-adding-a-rest-api-to-our-agentic-application-with-google-adk-6b87a4ea7567)

### Related ADK Articles

- [Give Your AI Agents Deep Understanding — Creating a Multi-Agent ADK Solution: Design Phase](https://medium.com/google-cloud/give-your-ai-agents-deep-understanding-creating-the-llms-txt-with-a-multi-agent-adk-solution-e5ae24bbd08b)
- [Using the Loop Pattern to Make My Multi-Agent Solution More Robust (with Google ADK)](https://medium.com/google-cloud/using-the-loop-pattern-to-make-my-multi-agent-solution-more-robust-86f8e9159a2a)

## Developing With This Repo

### Per Dev Session (Once One-Time Setup Tasks Have Been Completed)

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

### Using Direnv

Note that you can automate loading the `setup-env.sh` script by installing [direnv](https://direnv.net/), and then including the `.envrc` in the project folder. E.g.

```bash
sudo apt install direnv

# Add eval "$(direnv hook bash)" to your .bashrc
echo "eval \"\$(direnv hook bash)\"" >> ~/.bashrc

# Then, from this project folder:
direnv allow
```

### Useful Commands

| Command                       | Description                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| `source scripts/setup-env.sh` | Setup Google Cloud project and auth with Dev/Staging. Parameter options:<br> `[--noauth] [-t\|--target-env <DEV\|PROD>]` |
| `make install`                | Install all required dependencies using `uv` |
| `make playground`             | Launch ADK UI for testing agent locally and remotely. This runs `uv run adk web src` |
| `make api`                    | Launch the FastAPI backend:<br>`uv run fastapi dev src/main.py`|
| `make streamlit`              | Run Streamlit FE:<br>`MOCK_AUTH_USER="mock.user@example.com" uv run streamlit run src/streamlit_fe/app.py`|
| `make docker-adk`             | Launch ADK UI in Docker |
| `make docker-streamlit`       | Run Streamlit FE in Docker |
| `make docker-frontend`        | Launch React Frontend in Docker |
| `make docker-backend`         | Launch API and Backend in Docker |
| `make docker-front-and-back`  | Launch all services (frontend + backend) in Docker |
| `make docker-unified`         | Launch Unified Container (Frontend + Backend in one) |
| `make docker-clean`           | Remove any orphaned containers |
| `make test`                   | Run unit tests |
| `make test-all`               | Run unit and integration tests (takes a little longer) |
| `make test-ui`                | Run frontend UI tests (equivalent to `npm test` in `src/nextjs_fe`) |
| `make lint`                   | Run code quality checks (codespell, ruff, mypy) |
| `make terraform`              | Plan Terraform, prompt for authorisation, then apply |
| `uv run jupyter lab`          | Launch Jupyter notebook |

For full command options and usage, refer to the [Makefile](Makefile).

### Notebooks

The `notebooks/` directory contains Jupyter notebooks used for development and management tasks that are not part of the core application deployment.

#### File Search Store Management

The `notebooks/file_search_store.ipynb` notebook is used to manage the **File Search Store** for the Rickbot agent. This store is used for RAG (Retrieval Augmented Generation) to provide specific personas with access to reference documents.

> [!NOTE]
> The File Search Store is a feature of the **Gemini Developer API**. It is compatible with the `google-genai` SDK (version >= 1.49.0) but does not currently work with Vertex AI. Therefore, this notebook enables specific environment configurations to interact with the Gemini Developer API directly for store management.

###  Testing

- All tests are in the `src/tests` folder.
- The tests and how to run them are documented in `docs/testing.md`.

### Running ADK Dev Tools

With ADK CLI:

```bash
uv run adk run src/rickbot_agent
```

With ADK Web GUI:

```bash
# Last param is the location of the agents
uv run adk web src

# Or we can use the Agent Starter Git make aliases
make install && make playground
```

### Running the Full Stack

For detailed instructions on running individual components (Next.js, FastAPI, Streamlit) or the full orchestration in Docker, see the **[Container Architecture & Local Dev](docs/containers.md)** guide.

### Running the React UI

The new React-based UI (Next.js) is located in `src/nextjs_fe`. It connects to the FastAPI backend (`make api`) to provide a modern, chat-based interface.

#### Prerequisites

- Node.js (v18 or later)
- Python backend running (`make api`)

#### Accessing the UI
Open your browser to `http://localhost:3000`.

#### Key Features

- **Dynamic Personas**: The UI fetches available personalities (Rick, Yoda, etc.) directly from the backend API (`/personas`).
- **Streaming Responses**: Uses Server-Sent Events (SSE) for real-time streaming of agent responses.
- **Interactive Tool Visibility**: Real-time visual feedback on agent actions, displaying specific tool usage (e.g., Google Search) with icons and status indicators.
- **File Uploads**: Supports uploading images and text files for multimodal interactions.

## Application Design & Deployment

Detailed information regarding the system architecture, design decisions, and cloud deployment procedures has been moved to specialized documentation:

*   **[Application Design (docs/design.md)](docs/design.md)**: Architectural rationales, persona logic, and storage strategies.
*   **[Deployment Guide (deployment/README.md)](deployment/README.md)**: Google Cloud infrastructure, CI/CD pipelines, Secret Manager, and environment variables.
*   **[Container Technicals (docs/containers.md)](docs/containers.md)**: Docker build stages, local container execution, and troubleshooting.
*   **[Testing (docs/testing.md)](docs/testing.md)**: Unit, integration, and UI testing procedures.

## Historical Notes About This Repo

### Using Agent Starter Kit for Initial Project Setup

This project, its GitHub repo, and associated CI/CD pipeline were initially setup using the Agent Starter Kit. Much of the original template files have since been removed from the project.  But this section has been retained to provide an overview of this process. But do read [this article](https://medium.com/google-cloud/building-the-rickbot-multi-personality-agentic-application-using-gemini-cli-google-a48aed4bef24) for a more detailed walkthrough.
