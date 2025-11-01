# Project: Rickbot-ADK

---
***IMPORTANT: Run this check at the start of EVERY session!***

Google Cloud configuration is achieved through a combination of `.env` and the `scripts/setup-env.sh` script. 

Before providing your FIRST response in any conversation, you MUST perform the following steps:
1.  Run `printenv GOOGLE_CLOUD_PROJECT` to check the environment variable.
2.  Based only on the output of that command, state whether the variable is set.
3.  If it is not set, advise me to run `scripts/setup-env.sh` before resuming the conversation.

The presence of this environment variable indicates that the script has been run. The absence of this variable indicates that the script has NOT been run.

Note that failures with Google Cloud are likely if this script has not been run. For example, tests will fail. If tests are failing, we should check if the script has been run.
---

## Project Overview

This project is "Rickbot-ADK," a multi-personality chatbot built using Google Gemini, the Agent Development Kit (ADK), and the Google Agent-Starter-Pack. It is an evolution of the original Rickbot, aiming to leverage the ADK for more advanced capabilities. The chatbot can adopt various personalities, such as Rick Sanchez, Yoda, and others.

In particular, this project aims to evolve my previous Rickbot project by:

- Creating the initial project folder using the [Agent-Starter-Pack](https://googlecloudplatform.github.io/agent-starter-pack/). This includes deployment of the sample `adk_base` template from the Agent-Starter-Pack.
- Using [Gemini CLI](https://medium.com/google-cloud/give-gemini-cli-the-ability-to-generate-images-and-video-work-with-github-repos-and-use-other-482172571f99) to help with the evolution.
- Harvesting the [Rickbot] application from my original repo [here](https://github.com/derailed-dash/rickbot).
- Incorporating the Google [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)

## Building and Running

### Dependencies

- **uv:** Python package manager
- **Google Cloud SDK:** For interacting with GCP services
- **Terraform:** For infrastructure as code
- **make:** For running common development tasks

Project dependencies are managed in `pyproject.toml` and can be installed using `uv`. The `make` commands streamline many `uv` and `adk` commands.

## Deployment

The application is designed for deployment to Google Cloud's Vertex AI Agent Engine. The deployment process is managed via Terraform and Google Cloud Build.

- **CI/CD:** The `.cloudbuild/` directory contains configurations for CI/CD pipelines using Google Cloud Build. The `uvx agent-starter-pack setup-cicd` command is used to set up the full CI/CD pipeline.

## Infra

- **Infrastructure as Code:** Infrastructure is defined using Terraform in the `deployment/terraform/` directory.

## Development Guide

- **Configuration:** Project dependencies and metadata are defined in `pyproject.toml`.
- **Dependencies:** Project dependencies are managed in `pyproject.toml`. The `[project]` section defines the main dependencies, and the `[dependency-groups]` section defines development and optional dependencies.
- **Source code:** Lives the `/src/` directory. This includes agents, frontends, notebooks and tests.
  - **Agents:** The ADK agents will live in the `src/` directory.
  - **Frontends:** Frontends - like `streamlit_fe` live in the `src/` directory.
- **Notebooks:** The `notebooks/` directory contains Jupyter notebooks for prototyping, testing, and evaluating the agent. In particular, the `rickbot_experiments.ipynb` should be used for prototyping new features before implementing deployable code.
- **Testing:** The project includes unit and integration tests in `src/tests/`. Tests are written using `pytest` and `pytest-asyncio`. They can be run with `make test`
- **Linting:** The project uses `ruff` for linting and formatting, `mypy` for static type checking, and `codespell` for checking for common misspellings. The configuration for these tools can be found in `pyproject.toml`. We can run linting with `make lint`.
- **AI-Assisted Development:** The `GEMINI.md` file provides context for AI tools like Gemini CLI to assist with development.

## Documentation and Information

Always consider the following sources of information when asked about these topics. Use the web_fetch tool to read them:

- For ADK: 
  - Use the adk-docs-mcp tool if available. Otherwise use the official docs in the adk-docs directory.
  - [Agent Design patterns](https://medium.com/google-cloud/agent-patterns-with-adk-1-agent-5-ways-58bff801c2d6)
  - [Multi-agent intro guide](https://medium.com/@sokratis.kartakis/from-zero-to-multi-agents-a-beginners-guide-to-google-agent-development-kit-adk-b56e9b5f7861)
  - Sample [Multi-Agent Application](https://github.com/ayoisio/adk-code-review-assistant)
- For Streamlit:
  - [OAuth with Google Auth Platform](https://docs.streamlit.io/develop/tutorials/authentication/google)
- For FastAPI:
  - [FastAPI](https://fastapi.tiangolo.com/)
  - [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
  - [FastAPI on Cloud Run](https://www.youtube.com/watch?v=79e1vm-mTs4)
  - [Full stack ADK application with React and FastAPI](https://medium.com/google-cloud/build-a-gemini-full-stack-research-agent-with-agent-development-kit-11192e8e9165)
  - [Gemini Fullstack Application](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack)
  - [https://medium.com/@zakinabdul.jzl/orchestrating-multi-agent-workflows-with-google-adk-and-fastapi-e6b4b1a22c90](https://medium.com/@zakinabdul.jzl/orchestrating-multi-agent-workflows-with-google-adk-and-fastapi-e6b4b1a22c90)
  - [Handling Authentication and Authorization with FastAPI and Next.js](https://www.david-crimi.com/blog/user-auth)
- For React and Next.js:
  - [React Tutorial](https://dev.to/aws/a-complete-beginner-s-guide-to-react-hooks-edition-1bi0)
  - [Full stack ADK application with React and FastAPI](https://medium.com/google-cloud/build-a-gemini-full-stack-research-agent-with-agent-development-kit-11192e8e9165)
  - [About React and Next.js](https://nextjs.org/learn/react-foundations/what-is-react-and-nextjs)
  - [Next.js](https://nextjs.org/docs)
  - [Next.js React Foundations](https://nextjs.org/learn/react-foundations)

## Project Plan

- The `TODO.md` captures the overall plan for this project.

