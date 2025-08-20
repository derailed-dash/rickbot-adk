SHELL := /bin/bash

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter

# Launch local dev playground
playground:
	@echo "================================================================================="
	@echo "| 🚀 Starting your agent playground...                                          |"
	@echo "|                                                                               |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                           |"
	@echo "|                                                                               |"
	@echo "| 🔍 IMPORTANT: Select the 'adk_sample_app' folder to interact with your agent. |"
	@echo "================================================================================="
	uv run adk web --port 8501 src

# Launch local development server with hot-reload
local-backend:
	uv run uvicorn adk_sample_app.server:app --app-dir src --host 0.0.0.0 --port 8000 --reload

# Run unit and integration tests
test:
	uv run pytest src/tests/unit && uv run pytest src/tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# Run the programmatic test script
test-rickbot-standalone:
	uv run python scripts/test_rickbot_agent.py
