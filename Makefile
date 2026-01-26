SHELL := /bin/bash

# Hide unwanted messages - to use, just add ${GREP_FILTER} to any command
GREP_FILTER = 2>&1 | grep -v -e '^$$' -e 'WSL' -e 'xdg-open'

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter

# Launch local dev playground
adk-playground:
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

docker-streamlit: docker-clean
	@echo "================================================================================="
	@echo "| 🚀 Launching Streamlit FE in Docker                                           |"
	@echo "================================================================================="
	MOCK_AUTH_USER="mock.user@example.com" docker compose up streamlit_fe

docker-adk: docker-clean
	@echo "================================================================================="
	@echo "| 🚀 Launching Streamlit FE in Docker                                           |"
	@echo "================================================================================="
	MOCK_AUTH_USER="mock.user@example.com" docker compose up adk ${GREP_FILTER}

docker-clean:
	@echo "================================================================================="
	@echo "| 🚀 Cleaning orphaned containers                                               |"
	@echo "================================================================================="
	docker compose down --remove-orphans

# Run unit tests
test:
	@test -n "$(GOOGLE_CLOUD_PROJECT)" || (echo "Error: GOOGLE_CLOUD_PROJECT is not set. Setup environment before running tests" && exit 1)
	uv run pytest src/tests/unit

# Run unit and integration tests (takes a little longer)
test-all:
	@test -n "$(GOOGLE_CLOUD_PROJECT)" || (echo "Error: GOOGLE_CLOUD_PROJECT is not set. Setup environment before running tests" && exit 1)
	uv run pytest src/tests/unit && uv run pytest src/tests/integration

# Launch Next.js React UI
react-ui:
	cd src/nextjs_fe && npm run dev

# Run frontend UI tests
test-ui:
	cd src/nextjs_fe && npm test

# Run code quality checks (codespell, ruff, mypy)
lint:
	@echo "Running code quality checks..."
	uv sync --dev --extra jupyter --extra lint 
	uv run codespell -s
	uv run ruff check . --diff
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

api:
	@echo "================================================================================="
	@echo "| 🚀 Launching API frontend...                                                  |"
	@echo "|                                                                               |"
	@echo "| 📄 See docs at /docs                                                          |"
	@echo "================================================================================="
	# Using 'fastapi dev' for development with auto-reloading. For production, 'uvicorn' would be used directly.
	uv run fastapi dev src/main.py
