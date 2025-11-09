# ---- Builder Stage ----
# Creates a virtual environment with all necessary dependencies.
FROM python:3.12-slim AS builder

# Install uv by copying the binary from the official image. 
# This is faster and more reliable than installing it via pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project dependency definitions.
# This is done separately to leverage Docker's layer caching. 
# The next step will only be re-run if these files change.
COPY ./pyproject.toml ./uv.lock* ./

# Install dependencies into a virtual environment.
# We use --no-install-project to only install dependencies listed in pyproject.toml, not the project code itself. 
# This layer is cached.
# The --mount options provide access to the files and a cache directory
# without invalidating the layer cache on content changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the application source code to /app/src. 
# This is done after installing dependencies so we don't invalidate the dependency cache layer.
COPY ./src ./src

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ---- Final Stage ----
# Uses the virtual environment from the builder stage to create a smaller final image.
FROM python:3.12-slim

# Update OS packages to patch security vulnerabilities
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application source code from the builder stage
COPY --from=builder /app/src ./src

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Explicitly set the PYTHONPATH to the app directory to ensure modules are found
ENV PYTHONPATH="/app"

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

EXPOSE 8080

# The command is now relative to the new WORKDIR /app
CMD ["streamlit", "run", "src/streamlit_fe/app.py", "--server.port=8080", "--server.address=0.0.0.0"]