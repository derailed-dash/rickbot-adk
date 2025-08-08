"""
For deploying rickbot-adk to Vertex AI Agent Engine.

Wraps the core agent logic - defined in rickbot_agent/agent.py - into a deployable application.
"""

# mypy: disable-error-code="attr-defined,arg-type"
import copy
import datetime
import json
import logging
import os
from typing import Any

import google.auth
import vertexai
from google.adk.artifacts import GcsArtifactService
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from rickbot_agent.agent import root_agent
from rickbot_agent.utils.gcs import create_bucket_if_not_exists
from rickbot_agent.utils.tracing import CloudTraceLoggingSpanExporter
from rickbot_agent.utils.typing import Feedback


class AgentEngineApp(AdkApp):
    """
    Aplication Wrapper.
    This is the standard way to make an ADK agent compatible with the Vertex AI Agent Engine.
    """

    def set_up(self) -> None:
        """Set up logging and tracing for the agent engine app."""
        super().set_up()
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        provider = TracerProvider()
        processor = export.BatchSpanProcessor(
            CloudTraceLoggingSpanExporter(
                project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
            )
        )
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Registers the operations of the Agent.

        Extends the base operations to include feedback registration functionality.
        """
        operations = super().register_operations()
        operations[""] = operations[""] + ["register_feedback"]
        return operations

    def clone(self) -> "AgentEngineApp":
        """Returns a clone of the ADK application."""
        template_attributes = self._tmpl_attrs

        return self.__class__(
            agent=copy.deepcopy(template_attributes["agent"]),
            enable_tracing=bool(template_attributes.get("enable_tracing", False)),
            session_service_builder=template_attributes.get("session_service_builder"),
            artifact_service_builder=template_attributes.get(
                "artifact_service_builder"
            ),
            env_vars=template_attributes.get("env_vars"),
        )


def deploy_agent_engine_app(
    project: str,
    location: str,
    agent_name: str | None = None,
    requirements_file: str = ".requirements.txt",
    extra_packages: list[str] | None = None,
    env_vars: dict[str, str] | None = None,
) -> agent_engines.AgentEngine:
    """Deploy the agent engine app to Vertex AI.
    Creates the necessary Google Cloud Storage (GCS) buckets for staging the application code and storing artifacts
    (like files used in conversations).

    After a successful deployment it saves the agent's unique resource name to a deployment_metadata.json
    for other tools or scripts to reference.
    """
    if extra_packages is None:
        extra_packages = ["./rickbot_agent"]
    if env_vars is None:
        env_vars = {}

    staging_bucket_uri = f"gs://{project}-agent-engine"
    artifacts_bucket_name = f"{project}-rickbot-adk-logs-data"
    create_bucket_if_not_exists(
        bucket_name=artifacts_bucket_name, project=project, location=location
    )
    create_bucket_if_not_exists(
        bucket_name=staging_bucket_uri, project=project, location=location
    )

    vertexai.init(project=project, location=location, staging_bucket=staging_bucket_uri)

    # Read requirements
    with open(requirements_file, encoding="utf-8") as f:
        requirements = f.read().strip().split("\n")

    agent_engine = AgentEngineApp(
        agent=root_agent,
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name
        ),
    )

    # Set worker parallelism to 1
    env_vars["NUM_WORKERS"] = "1"

    # Common configuration for both create and update operations
    agent_config = {
        "agent_engine": agent_engine,
        "display_name": agent_name,
        "description": "A multi-personality chatbot built using Google Gemini and the Agent Development Kit (ADK)",
        "extra_packages": extra_packages,
        "env_vars": env_vars,
    }
    logging.info("Agent config: %s", agent_config)
    agent_config["requirements"] = requirements

    # Check if an agent with this name already exists
    existing_agents = list(agent_engines.list(filter=f"display_name={agent_name}"))
    if existing_agents:
        # Update the existing agent with new configuration
        logging.info("Updating existing agent: %s", agent_name)
        remote_agent = existing_agents[0].update(**agent_config)
    else:
        # Create a new agent if none exists
        logging.info("Creating new agent: %s", agent_name)
        remote_agent = agent_engines.create(**agent_config)

    config = {
        "remote_agent_engine_id": remote_agent.resource_name,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
    }
    config_file = "deployment_metadata.json"

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    logging.info("Agent Engine ID written to %s", config_file)

    return remote_agent


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy agent engine app to Vertex AI")
    parser.add_argument(
        "--project",
        default=None,
        help="GCP project ID (defaults to application default credentials)",
    )
    parser.add_argument(
        "--location",
        default="europe-west4",
        help="GCP region (defaults to europe-west4)",
    )
    parser.add_argument(
        "--agent-name",
        default="rickbot-adk",
        help="Name for the agent engine",
    )
    parser.add_argument(
        "--requirements-file",
        default=".requirements.txt",
        help="Path to requirements.txt file",
    )
    parser.add_argument(
        "--extra-packages",
        nargs="+",
        default=["./rickbot_agent"],
        help="Additional packages to include",
    )
    parser.add_argument(
        "--set-env-vars",
        help="Comma-separated list of environment variables in KEY=VALUE format",
    )
    args = parser.parse_args()

    # Parse environment variables if provided
    env_vars = {}
    if args.set_env_vars:
        for pair in args.set_env_vars.split(","):
            key, value = pair.split("=", 1)
            env_vars[key] = value

    if not args.project:
        _, args.project = google.auth.default()

    print(
        """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    )

    print(args)

    deploy_agent_engine_app(
        project=args.project,
        location=args.location,
        agent_name=args.agent_name,
        requirements_file=args.requirements_file,
        extra_packages=args.extra_packages,
        env_vars=env_vars,
    )
