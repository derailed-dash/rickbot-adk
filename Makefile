SHELL := /bin/bash

# Hide unwanted messages - to use, just add ${GREP_FILTER} to any command
GREP_FILTER = 2>&1 | grep -v -e '^$$' -e 'WSL' -e 'xdg-open'

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter

# Launch local dev playground
playground:
	@echo "================================================================================="
	@echo "| 🚀 Starting your agent playground...                                          |"
	@echo "|                                                                               |"
	@echo "| 🔍 Select your required agent and then interact                               |"
	@echo "================================================================================="
	uv run adk web --port 8501 src

streamlit:
	@echo "================================================================================="
	@echo "| 🚀 Launching Streamlit FE...                                                  |"
	@echo "================================================================================="
	MOCK_AUTH_USER="mock.user@example.com" uv run -- streamlit run src/streamlit_fe/app.py ${GREP_FILTER}

# Launch local development server with hot-reload
local-backend:
	uv run uvicorn adk_sample_app.server:app --app-dir src --host 0.0.0.0 --port 8000 --reload

# Run unit and integration tests
test:
	@test -n "$(GOOGLE_CLOUD_PROJECT)" || (echo "Error: GOOGLE_CLOUD_PROJECT is not set. Setup environment before running tests" && exit 1)
	uv run pytest src/tests/unit && uv run pytest src/tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra jupyter --extra lint 
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# Deploy infrastructure using Terraform
terraform:
	@echo "Running Terraform init and plan..."
	@(cd "deployment/terraform" && terraform init && terraform plan -var-file="vars/env.tfvars" -out=out.tfplan)	
	@echo "Terraform plan complete. Review the output above."
	@echo -n "Do you want to apply this plan? [y/n] " && read REPLY; \
	echo "(DEBUG: You entered '$$REPLY')"; \
	case "$$REPLY:-'n'" in \
		[Yy]*) \
			echo "Applying Terraform plan..."; \
			cd "deployment/terraform"; \
			terraform apply "out.tfplan";; \
		*) \
			echo "Terraform apply cancelled.";; \
	esac
