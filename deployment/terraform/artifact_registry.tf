# Create Artifact Registry repository for Docker images

resource "google_artifact_registry_repository" "repo" {
  location      = var.cb_region
  repository_id = var.repository_name
  description   = "Repo for Generative AI applications"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
