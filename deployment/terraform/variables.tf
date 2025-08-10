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
    "roles/iap.admin"
  ]
}

variable "cicd_sa_deployment_required_roles" {
  description = "List of roles to assign to the CICD runner service account for the Staging and Prod projects."
  type        = list(string)
  default = [
    "roles/run.developer",    
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}

variable "repository_name" {
  description = "The name for the Artifact Registry repository."
  type        = string
}

variable "repository_owner" {
  description = "Owner of the Git repository - username or organization"
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