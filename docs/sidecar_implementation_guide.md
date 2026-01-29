# Implementing Cloud Run Sidecars for Next.js and FastAPI

This guide details the design decisions and implementation steps taken to evolve the **Rickbot-ADK** project from a single-container Streamlit application to a modern, multi-container architecture using the **Cloud Run Sidecar pattern**.

This approach allows us to deploy a Next.js frontend (Node.js) and a FastAPI backend (Python) within a single Cloud Run service, sharing the same network namespace (`localhost`) and scaling characteristics, while maintaining separate, optimized build processes for each runtime.

## 1. Architectural Decision: The Sidecar Pattern

### The Problem
We wanted to introduce a modern React-based UI (Next.js) while keeping our robust Python agent backend (FastAPI + ADK).
- **Option A (Separate Services):** Deploying two separate Cloud Run services (Frontend & Backend) adds complexity:
    -   **Networking:** Requires CORS configuration, public internet traversal, or complex VPC peering.
    -   **Auth:** Sharing authentication state across domains is harder.
    -   **Cost:** Double the minimum instance count and potentially higher cold start overhead.
- **Option B (Monolithic Container):** Installing Node.js and Python in one massive container creates a bloated image (`> 2GB`), slow build times, and "dependency hell."

### The Solution: Sidecars
Cloud Run (Gen 2) supports multi-container deployments. We deploy two containers in one service:
1.  **Ingress Container (Next.js):** Handles public traffic (port 3000), serves the UI, and performs Server-Side Rendering (SSR).
2.  **Sidecar Container (FastAPI):** Runs the agent logic (port 8000). Not exposed publicly directly, but accessible to the Ingress container via `localhost:8000`.

**Benefits:**
- **Single Deployment Unit:** One Terraform resource, one URL.
- **Security:** Backend API is not exposed to the public internet; only the frontend can talk to it.
- **Performance:** Communication happens over loopback (no network latency).
- **Optimization:** Each container uses a base image optimized for its runtime (`node:20-slim` vs `python:3.12-slim`).

---

## 2. Containerization Strategy

We moved from a single `Dockerfile` to a multi-file strategy.

### Dockerfile.react_fe (The Frontend)
- **Base:** `node:20-slim`.
- **Optimization:** Uses a multi-stage build (`deps` -> `builder` -> `runner`).
- **Security:** Runs as a non-root user (`nextjs`).
- **Performance:** Copies only the necessary `.next/` build output and `public/` assets.
- **Key Trick:** We use `COPY --from=builder --chown=nextjs:nextjs ...` to avoid a slow `RUN chown -R` step at the end, saving ~40s on build time.

### Dockerfile.api_sidecar (The Backend)
- **Base:** `python:3.12-slim`.
- **Optimization:** Uses `uv` for ultra-fast Python package installation in a builder stage.
- **Runtime:** Copies the virtual environment (`.venv`) from the builder.
- **Command:** Runs `fastapi run` instead of Streamlit.

---

## 3. Local Development (Simulation)

To simulate the Cloud Run environment locally, we updated `docker-compose.yml` to use `network_mode: service:api_sidecar`.

```yaml
  api_sidecar:
    # ... (FastAPI config)
    ports:
      - "3000:3000" # Expose Next.js port
      - "8000:8000" # Expose FastAPI port

  react_fe:
    # ... (Next.js config)
    network_mode: "service:api_sidecar" # <--- The Magic
    depends_on:
      - api_sidecar
```

By telling `react_fe` to use the network stack of `api_sidecar`, they share `localhost`. The Next.js app can call `http://localhost:8000` just like it will in production.

**Command:** `make docker-react`

---

## 4. Infrastructure as Code (Terraform)

We updated Terraform to support a toggleable deployment (`ui_type`).

### Dynamic Containers
In `deployment/terraform/locals.tf`, we defined two configurations:

```hcl
  containers = var.ui_type == "react" ? [
    {
      name  = "ingress"
      image = "..." 
      # ... Next.js config
    },
    {
      name  = "api-sidecar"
      image = "..."
      # ... FastAPI config
    }
  ] : [
    {
      name  = "streamlit"
      # ... Legacy config
    }
  ]
```

In `service.tf`, we use a `dynamic "containers"` block to render the correct configuration based on the `ui_type` variable.

### Resource Optimization

To manage costs, we tuned the resource limits for the Sidecar deployment to match the legacy cost profile (Total: ~1 CPU, ~2GB RAM):
- **Next.js:** 0.2 CPU, 512 MiB RAM.
- **FastAPI:** 0.8 CPU, 1.5 GiB RAM.

---

## 5. CI/CD Pipeline (Cloud Build)

We updated `.cloudbuild/staging.yaml` and `deploy-to-prod.yaml` to handle the conditional build logic.

1.  **Conditional Building:** The pipeline uses `Kaniko` to build *both* `Dockerfile.react_fe` and `Dockerfile.api_sidecar` if needed.
2.  **Dynamic Deployment:** We use a shell script block in the deployment step to check `$_UI_TYPE`.
    -   **If React:** It generates a `service.yaml` on the fly (allowing for multi-container definitions) and deploys using `gcloud beta run services replace`.
    -   **If Streamlit:** It runs the standard `gcloud run deploy` command.
3.  **Environment Configuration:** We injected a dynamic `_APP_URL` variable to ensure the Next.js `NEXTAUTH_URL` matches the target environment (Staging vs. Prod).

---

## Summary of Steps to Replicate

1.  **Code Prep:** Ensure Frontend (`src/nextjs_fe`) and Backend (`src/main.py`) are ready.
2.  **Dockerfiles:** Create optimized, multi-stage Dockerfiles for each.
3.  **Local Dev:** Configure `docker-compose` with shared networking to prove `localhost` communication works.
4.  **Terraform:** Abstract the container definition in `locals.tf` and use `dynamic` blocks in `service.tf`.
5.  **Cloud Build:** Update YAMLs to build multiple images and use a conditional deployment script to apply the correct Cloud Run configuration.
