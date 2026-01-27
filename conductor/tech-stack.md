# Tech Stack: Rickbot-ADK

## Backend
- **Language:** Python 3.12+ (managed with `uv`).
- **Frameworks:** 
    - **Google Agent Development Kit (ADK):** Core framework for building and managing the multi-personality agents.
    - **FastAPI**: High-performance web framework for the backend API, decoupling agent logic from the frontends.
    - **Authlib**: For handling OAuth flows and JWT token verification.
    - **SlowAPI**: For implementing robust API rate limiting and ensuring system stability.
- **SDKs:** 
    - **Google Gen AI SDK (`google-genai`):** For direct interaction with Gemini models.
    - **Google Cloud SDKs:** Including Vertex AI, Secret Manager, and Logging/Tracing.

## Frontend
- **Main UI:** **Next.js (React/TypeScript).** A modern, responsive web application for the primary chat interface.
- **Authentication:** **NextAuth.js.** For handling client-side OAuth sessions and secure communication with the backend.
- **Internal/Admin UI:** **Streamlit.** Used for rapid prototyping and internal testing of agent behaviors.
- **Styling:** **MUI (Material UI), Tailwind CSS, and Framer Motion.** For a polished, animated, and consistent visual design.

## Infrastructure & DevOps
- **Cloud Provider:** **Google Cloud Platform (GCP).**
- **Hosting:** **Cloud Run / Vertex AI Agent Engine.**
- **Infrastructure as Code (IaC):** **Terraform.** For reproducible environment setup.
- **CI/CD:** **Google Cloud Build.** Automating tests and deployments.
- **Containerization:** **Docker.** For consistent environments across development and production.
- **Dependency Management:** **`uv`.** Used for fast and reliable Python package management.

## Monitoring & Observability
- **Observability:** **OpenTelemetry.** Integrating with Google Cloud Tracing and Logging for performance monitoring and debugging.
