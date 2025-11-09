FROM python:3.12-slim

# Update OS packages to patch security vulnerabilities
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy project definition and lock files first
COPY ./pyproject.toml ./uv.lock* ./

# Install dependencies in the root
RUN uv sync --frozen

# Copy the entire src directory
COPY ./src ./

# Explicitly set the PYTHONPATH to the app directory to ensure modules are found
ARG PYTHONPATH=""
ENV PYTHONPATH="/app"

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

EXPOSE 8080

# The command is now relative to the new WORKDIR /app/src
CMD ["uv", "run", "--", "streamlit", "run", "streamlit_fe/app.py", "--server.port=8080", "--server.address=0.0.0.0"]