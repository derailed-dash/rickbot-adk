# Container Architecture Walkthrough

This document details the containerization strategy for the Rickbot application, explaining how the different components are built, orchestrated, and run.

## Overview

The application is composed of three main services when running locally or in production:

1.  **Frontend (React/Next.js)**: The modern user interface.
2.  **Backend (FastAPI)**: The central agent API.
3.  **Streamlit UI (Legacy)**: The original prototype interface (optional).

We use **Docker** for containerization and **Docker Compose** for local orchestration.

## Dockerfiles

We utilize optimized Dockerfiles for each service to ensure minimal image sizes and secure execution.

### 1. Backend (`Dockerfile.api`)

This Dockerfile builds the Python FastAPI backend.

*   **Base Image**: `python:3.12-slim` for a small footprint.
*   **Multi-Stage Build**:
    *   **Builder Stage**: Installs dependencies using `uv` (an extremely fast Python package manager) into a virtual environment.
    *   **Final Stage**: Copies the virtual environment and only the necessary source code (`src/main.py`, `src/rickbot_agent/`, `src/rickbot_utils/`) from the builder.
*   **Whitelist Approach**: We explicitly copy only the required backend code, excluding the frontend source directories (`src/nextjs_fe`, `src/streamlit_fe`) to keep the image clean.
*   **Security**: Runs as a non-root user `app-user`.

### 2. Frontend (`src/nextjs_fe/Dockerfile`)

This Dockerfile builds the Next.js frontend application.

*   **Base Image**: `node:18-alpine`.
*   **Multi-Stage Build**:
    *   **Deps**: Installs dependencies (`npm ci`).
    *   **Builder**: Builds the Next.js application (`npm run build`). It accepts `NEXT_PUBLIC_API_URL` as a build argument to bake in the API endpoint.
    *   **Runner**: A lightweight production image that runs the app.
*   **Standalone Output**: We use Next.js's `output: 'standalone'` feature (configured in `next.config.js`) to automatically trace and include only the necessary files for production, significantly reducing image size.
*   **Security**: Runs as a non-root user `nextjs`.

### 3. Streamlit UI (`Dockerfile.streamlit`)

This file builds the legacy Streamlit interface (and is also used by the ADK web playground).

*   **Original Name:** `Dockerfile` (Renamed to `Dockerfile.streamlit` for clarity).
*   **Base Image**: `python:3.12-slim`.
*   **Usage**: Used for the `streamlit_fe` service and CI/CD pipelines (until they are fully migrated to the sidecar pattern).

### 4. Unified Container (`Dockerfile.unified`)

This Dockerfile combines both the Frontend and Backend into a single image, providing a simplified deployment option.

#### Design Philosophy

The unified container was created to address several deployment scenarios:

1.  **Simplified Cloud Run Deployment**: Cloud Run excels at running single containers. While multi-container deployments are possible via sidecars, a unified image simplifies configuration and reduces networking complexity.
2.  **Local Development**: Developers can run the entire stack with a single `docker run` command or `make docker-unified`, without needing Docker Compose.
3.  **Resource Efficiency**: Combining services reduces the overhead of running multiple containers and eliminates inter-container networking latency.

#### Build Strategy

The `Dockerfile.unified` uses a **three-stage build** process:

1.  **Backend Builder Stage** (`backend-builder`):
    *   Base: `python:3.12-slim`
    *   Installs Python dependencies using `uv sync --locked --no-dev`
    *   Whitelists only backend code (`src/main.py`, `src/rickbot_agent/`, `src/rickbot_utils/`)
    *   Creates a `.venv` with production dependencies

2.  **Frontend Builder Stage** (`frontend-builder`):
    *   Base: `node:18-alpine`
    *   Installs Node.js dependencies via `npm ci`
    *   Builds Next.js in standalone mode (`npm run build`)
    *   Outputs a minimal production bundle in `.next/standalone/`

3.  **Final Unified Stage**:
    *   Base: `python:3.12-slim`
    *   Installs Node.js runtime (required for Next.js)
    *   Copies backend `.venv` and source from `backend-builder`
    *   Copies frontend standalone bundle from `frontend-builder`
    *   Uses `scripts/start-unified.sh` to orchestrate both processes

#### Inter-Process Communication

The unified container avoids the need for Nginx or complex networking:

*   **Backend**: Runs on `http://127.0.0.1:8000` (localhost only)
*   **Frontend**: Runs on `http://0.0.0.0:8080` (exposed externally)
*   **Proxying**: Next.js's `rewrites` feature (in `next.config.js`) proxies API requests (`/chat`, `/personas`) to the backend:
    ```javascript
    async rewrites() {
      return [
        {
          source: '/chat',
          destination: 'http://127.0.0.1:8000/chat',
        },
        // ...
      ];
    }
    ```

This eliminates the need for an Nginx sidecar while maintaining clean separation of concerns.

#### Dependency Optimization

A key challenge in creating the unified container was managing Python dependencies. The initial build included **all** project dependencies, including heavy packages like:

*   `streamlit` (~50MB)
*   `langchain` and related packages (~100-150MB)
*   `pandas` (transitive dependency of streamlit)

These were only needed for the legacy Streamlit UI, not the core backend or unified container.

**Solution**: We refactored `pyproject.toml` to use **optional dependency groups**:

```toml
[project.dependencies]
# Core dependencies only (FastAPI, ADK, etc.)

[project.optional-dependencies]
streamlit = [
    "streamlit",
    "langchain",
    "langchain-core",
    "streamlit-feedback",
    "langchain-google-vertexai",
]
```

With this structure:

*   `Dockerfile.unified` and `Dockerfile.api` use `uv sync --no-dev` (excludes optional deps)
*   `Dockerfile.streamlit` uses `uv sync --extra streamlit` (includes them)
*   Local development uses `make install` which runs `uv sync --extra streamlit` for full feature access

**Result**: The unified container size was reduced by around 200MB.

#### Process Management

The `scripts/start-unified.sh` script handles process orchestration:

1.  Starts FastAPI in the background on port 8000
2.  Waits for FastAPI to be ready (health check loop)
3.  Starts Next.js in the foreground on port 8080

Running Next.js in the foreground ensures the container stays alive and logs are properly captured.

#### Security

*   Runs as non-root user `app-user`
*   Minimal base image (`python:3.12-slim`)
*   Whitelisted file copying (no accidental inclusion of secrets or dev files)
*   Production-only dependencies (`--no-dev`)

The `docker-compose.yml` file orchestrates these services for a seamless local development experience that mirrors our production architecture.

### Services

*   **`backend`**:
    *   Builds from `Dockerfile.api`.
    *   Exposes port `8080`.
    *   Mounts the local `src` directory for live reloading during development (though full rebuilds are safer for structural changes).
    *   Mounts Google Cloud credentials (ADC) to allow access to Vertex AI and Secret Manager.
    *   Sets `BACKEND_ALLOW_MOCK_AUTH=true` to enable local testing without real OAuth.

*   **`frontend`**:
    *   Builds from `src/nextjs_fe/Dockerfile`.
    *   Exposes port `3000`.
    *   **Critical Configuration**: Passes `NEXT_PUBLIC_API_URL: http://localhost:8080` as a build argument. This ensures the client-side React app knows where to find the API (which is mapped to localhost:8080 by Docker Compose).
    *   **Environment Variables**: Loads secrets (like `NEXTAUTH_SECRET`, OAuth credentials) and configuration directly from `src/nextjs_fe/.env.local` via the `env_file` directive.
    *   Configured for Mock Auth by default (`NEXT_PUBLIC_ALLOW_MOCK_AUTH=true`).

*   **`streamlit_fe`**:
    *   Legacy interface, also available for testing.
    *   Builds from `Dockerfile.streamlit`.
    *   Exposes port `8501`.

### Running the Environment

To start the full stack:

```bash
docker compose up -d --build backend frontend
```

Alternatively, you can use the Makefile convenience command:

```bash
make docker-front-and-back
```

You can also run services individually:

```bash
make docker-backend
make docker-frontend
```

*   **Frontend**: Access at [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs**: Access at [http://localhost:8080/docs](http://localhost:8080/docs)

### Troubleshooting

*   **"Not Authenticated"**: Ensure you are logged in (Mock Login works locally).
*   **API Connection Failed**: Check if the backend container is running (`docker ps`) and accessible at `http://localhost:8080`. If the frontend cannot reach it, ensure `NEXT_PUBLIC_API_URL` was correctly set during the build (try rebuilding with `--build`).
*   **Permissions Errors**: If the backend logs show permission errors accessing Google Cloud resources (like Secret Manager), ensure your local Application Default Credentials are set up and that the `GOOGLE_CLOUD_PROJECT` environment variable in `.env` matches the project your credentials have access to.

## Evolution & Troubleshooting: The Unified Container Journey

Transitioning from "Two Separate Containers" to a "Unified Container" introduced unexpected behaviors, primarily because it fundamentally changed how traffic reaches the backend API.

### The Architecture Shift

1.  **Two Separate Containers (Direct Access)**:
    *   In the original architecture, the browser communicates with two distinct endpoints:
        *   **Frontend**: `http://localhost:3000` (Next.js)
        *   **Backend**: `http://localhost:8080` (FastAPI)
    *   **Traffic Flow**: The browser sends chat requests *directly* to FastAPI. There is no middleman. Streaming responses flow directly to the client.

2.  **Unified Container (Proxied Access)**:
    *   In the unified container, only **one port** is exposed (e.g., 8080).
    *   The browser sends all requests to the Next.js server. Next.js then *proxies* API requests to the backend (running on `localhost:8000` inside the container).
    *   **Traffic Flow**: User -> Next.js (Node server) -> FastAPI.
    *   **Impact**: This introduces a Node.js proxy layer into the real-time chat stream.

### Compatibility Challenges

This introduction of the proxy layer revealed two critical issues that were masked in the "Separate Containers" setup:

#### 1. The "Silence" Problem (SSE Buffering)

*   **Symptom**: The UI would remain stuck in the "Thinking..." state, failing to show granular updates (like "Searching Google..." or "Using RagAgent..."), even though the backend was generating them.
*   **Cause**: The Node.js proxy buffered the small Server-Sent Events (SSE) chunks coming from FastAPI. Unlike the browser, which consumes streams immediately, the proxy waited to fill a buffer before flushing data to the client, effectively silencing the real-time feedback loop.
*   **Solution**: We implemented a robust two-layer fix:
    1.  **Headers**: Added `X-Accel-Buffering: no` and `Cache-Control: no-cache` to the `src/main.py` response. This explicitly instructs proxies (like Nginx) to disable buffering for the stream.
    2.  **Protocol Padding**: As a failsafe, we append 4KB of whitespace padding (`SSE_FLUSH_PADDING_BYTES = 4096`) to critical events. This forces any recalcitrant proxy buffers (like Next.js rewrites) to flush immediately, ensuring "Thinking" updates are visible instantly.

#### 2. The "Hang" Problem (RAG Timeouts)

*   **Symptom**: When the agent attempted to use the `RagAgent` (File Search), the request would simply hang indefinitely in the UI until eventually failing (or timing out), with no response ever received.
*   **Cause**: RAG operations are time-intensive (initializing the store, uploading files, waiting for indexing). The implicit timeouts in the containerized networking stack (and the `google-genai` client defaults) were shorter than the operation duration, causing the connection to be silently dropped or the client to give up before the result was ready.
*   **Solution**:
    *   **Monkey-Patching**: We patched `genai.Client` in `src/rickbot_agent/agent.py` to enforce `http_options={'timeout': 60}` (60 seconds).
    *   **Explicit Timeouts**: This ensured the underlying gRPC transport remained open long enough for the complex RAG operations to complete, eliminating the hangs.

### A Note on Sidecar Applicability

It is important to note that these challenges are not unique to the Unified Container strategy. If we had chosen the **Sidecar Pattern**, we would likely have encountered the same issues:

*   **Buffering**: A sidecar setup typically proxies traffic via the frontend (ingress) to the backend (localhost sidecar), retaining the Node.js proxy layer that caused the buffering.
*   **Timeouts**: The RAG timeout is intrinsic to the long-running nature of the operation and the networking defaults in Cloud Run limitations; separating the containers would not automatically resolve the client library's timeout behavior.

Therefore, the fixes implemented (Padding and explicit Timeouts) are robust architectural improvements beneficial for *any* containerized deployment of this stack.

### Validated Patterns

Our solutions align with industry standard workarounds for these specific proxy and gRPC challenges:

*   **SSE Padding**: 
    *   [Buffer-defeating with padding (Stack Overflow)](https://stackoverflow.com/questions/13386681/streaming-data-with-php-and-nginx-fastcgi-flush-behavior)
    *   [Nginx Proxy Buffering (ServerFault)](https://serverfault.com/questions/801628/for-server-sent-events-sse-what-nginx-configuration-is-required)
*   **gRPC Timeouts**:
    *   [Cloud Run gRPC Timeouts (Google Cloud Docs)](https://cloud.google.com/run/docs/troubleshooting#504)
    *   [gRPC Client Timeout Best Practices (gRPC.io)](https://grpc.io/docs/guides/deadlines/)

## Lessons Learned

### Dependency Management

1.  **Optional Dependencies Are Essential**: For projects with multiple deployment targets (unified, backend-only, Streamlit), using `[project.optional-dependencies]` prevents bloat in production images.
2.  **CI/CD Must Match**: When moving dependencies to optional groups, update CI/CD pipelines (e.g., `.cloudbuild/pr_checks.yaml`) to install the necessary extras for testing.
3.  **Local Dev vs Production**: Use `make install` to install all extras locally for full feature access, while production builds remain lean.

### Multi-Stage Builds

1.  **Layer Caching**: Order Dockerfile commands from least-to-most frequently changing (dependencies before source code) to maximize cache hits.
2.  **Whitelist, Don't Blacklist**: Explicitly `COPY` only what's needed rather than copying everything and excluding files. This prevents accidental inclusion of sensitive data.
3.  **Build Arguments**: Use `ARG` for configuration that changes between environments (e.g., `NEXT_PUBLIC_API_URL`).

### Unified Container Trade-offs

**Pros**:
*   Simpler deployment (single artifact)
*   Reduced networking overhead
*   Easier local testing

**Cons**:
*   Larger image size than backend-only (includes Node.js runtime)
*   Less granular scaling (can't scale frontend and backend independently)
*   More complex startup orchestration

**When to Use**:
*   Cloud Run deployments where simplicity is prioritized
*   Development/staging environments
*   Low-to-medium traffic applications

**When to Use Separate Containers**:
*   High-traffic production environments requiring independent scaling
*   Kubernetes deployments with sophisticated orchestration
*   When frontend and backend have different resource requirements
