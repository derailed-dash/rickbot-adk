variable "project_name" {
  type        = string
  description = "Project name used as a base for resource naming"
  default     = "rickbot-adk"
}

variable "prod_project_id" {
  type        = string
  description = "**Production** Google Cloud Project ID for resource deployment."
}

variable "staging_project_id" {
  type        = string
  description = "**Staging** Google Cloud Project ID for resource deployment."
}

variable "cicd_runner_project_id" {
  type        = string
  description = "Google Cloud Project ID where CI/CD pipelines will execute."
}

variable "my_org" {
  description = "Your organization's domain (e.g., example.com)."
  type        = string
}

variable "region" {
  type        = string
  description = "Google Cloud region for resource deployment."
  default     = "europe-west4"
}

variable "cb_region" {
  description = "The Google Cloud region where Cloud Build will run."
  type        = string
  default     = "europe-west1"
}

variable "service_name" {
  description = "The name for the Cloud Run service and related resources."
  type        = string
}

variable "staging_app_domain_name" {
  description = "A list of domain names to be mapped to the service"
  type        = list(string)
}

variable "prod_app_domain_name" {
  description = "A list of domain names to be mapped to the service"
  type        = list(string)
}

variable "app_name" {
  description = "The name of the UI client application"
  type        = string
  default     = "rickbot_st_ui"
}

variable "agent_name" {
  description = "The name of the Ricbot agent"
  type        = string
  default     = "rickbot_agent"
}

variable "google_genai_use_vertexai" {
  description = "Whether to use Vertex AI for auth, rather than API Key"
  type        = bool
  default     = false
}

variable "model" {
  description = "The model used by the agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "log_level" {
  description = "Logging level."
  type        = string
  default     = "INFO"
}

variable "host_connection_name" {
  description = "Name of the host connection to create in Cloud Build"
  type        = string
  default     = "rickbot-adk-github-connection"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "Log Sink filter for capturing telemetry data. Captures logs with the `traceloop.association.properties.log_type` attribute set to `tracing`."
  default     = "labels.service_name=\"rickbot-adk\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "Log Sink filter for capturing feedback data. Captures logs where the `log_type` field is `feedback`."
  default     = "jsonPayload.log_type=\"feedback\""
}

variable "app_sa_roles" {
  description = "List of roles to assign to the application service account"
  type        = list(string)
  default = [
    "roles/secretmanager.secretAccessor",
    "roles/aiplatform.user",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/storage.admin",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/datastore.user",
  ]
}

variable "cicd_roles" {
  description = "List of roles to assign to the CICD runner service account in the CICD project"
  type        = list(string)
  default = [
    "roles/run.admin",
    "roles/run.invoker",
    "roles/iam.serviceAccountAdmin",
    "roles/storage.admin",
    "roles/aiplatform.user",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/artifactregistry.writer",
    "roles/cloudbuild.builds.builder",
    "roles/iap.admin",
    "roles/datastore.user",
  ]
}

variable "cicd_sa_deployment_required_roles" {
  description = "List of roles to assign to the CICD runner service account for the Staging and Prod projects."
  type        = list(string)
  default = [
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin",
    "roles/iap.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/datastore.user",
  ]
}

variable "repository_name" {
  description = "The name for the GitHub repository."
  type        = string
}

variable "repository_owner" {
  description = "Owner of the Git repository - username or organization"
  type        = string
}

variable "repository_desc" {
  description = "Description of the GitHub repo"
  type        = string
}

variable "github_app_installation_id" {
  description = "GitHub App Installation ID for Cloud Build"
  type        = string
  default     = null
}


variable "github_pat_secret_id" {
  description = "GitHub PAT Secret ID created by gcloud CLI"
  type        = string
  default     = null
}

variable "create_cb_connection" {
  description = "Flag indicating if a Cloud Build connection already exists"
  type        = bool
  default     = false
}

variable "create_repository" {
  description = "Flag indicating whether to create a new Git repository"
  type        = bool
  default     = false
}

variable "artifact_repo_name" {
  description = "The name for the Artifact Registry repository."
  type        = string
}

variable "rate_limit" {
  description = "Rate limit for the application (e.g., '60 per minute')."
  type        = string
  default     = "60"
}

variable "auth_required" {
  description = "Whether authentication is required for the application."
  type        = string # Cloud Build expects string "True"/"False"
  default     = "True"
}

variable "google_cloud_location" {
  description = "Google Cloud Location for GenAI resources (e.g., 'global')."
  type        = string
  default     = "global"
}

variable "staging_min_instances" {
  description = "Minimum number of instances for the Staging Cloud Run service."
  type        = number
  default     = 0
}

variable "staging_max_instances" {
  description = "Maximum number of instances for the Staging Cloud Run service."
  type        = number
  default     = 1
}

variable "prod_min_instances" {
  description = "Minimum number of instances for the Prod Cloud Run service."
  type        = number
  default     = 0
}

variable "prod_max_instances" {
  description = "Maximum number of instances for the Prod Cloud Run service."
  type        = number
  default     = 1
}

variable "GOOGLE_CLIENT_ID_STAGING" {
  description = "Google Client ID for Staging environment"
  type        = string
}

variable "GOOGLE_CLIENT_ID_PROD" {
  description = "Google Client ID for Production environment"
  type        = string
}

variable "GITHUB_CLIENT_ID_STAGING" {
  description = "GitHub Client ID for Staging environment"
  type        = string
}

variable "GITHUB_CLIENT_ID_PROD" {
  description = "GitHub Client ID for Production environment"
  type        = string
}
