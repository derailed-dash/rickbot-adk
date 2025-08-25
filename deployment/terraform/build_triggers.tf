# a. Create PR checks trigger
resource "google_cloudbuild_trigger" "pr_checks" {
  name            = "pr-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.cb_region
  description     = "Trigger for PR checks"
  service_account = resource.google_service_account.cicd_runner_sa.id

  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.cb_region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    pull_request {
      branch = "main"
    }
  }

  filename = ".cloudbuild/pr_checks.yaml"
  included_files = [
    "src/**",
    "data_ingestion/**",
    "deployment/**",
    "uv.lock",
  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  depends_on = [
    resource.google_project_service.cicd_services, 
    resource.google_project_service.deploy_project_services, 
    google_cloudbuildv2_connection.github_connection, 
    google_cloudbuildv2_repository.repo
  ]
}

# b. Create CD pipeline trigger
resource "google_cloudbuild_trigger" "cd_pipeline" {
  name            = "cd-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.cb_region # Cloud Build has quota restrictions in certain regions
  service_account = resource.google_service_account.cicd_runner_sa.id
  description     = "Trigger for CD pipeline"

  repository_event_config {
    # GitHub repo connection
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.cb_region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    push {
      branch = "main"
    }
  }

  filename = ".cloudbuild/staging.yaml"
  included_files = [
    "src/**",
    "data_ingestion/**",
    "deployment/**",
    "uv.lock"
  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  substitutions = {
    _STAGING_PROJECT_ID            = var.staging_project_id
    _BUCKET_NAME_LOAD_TEST_RESULTS = resource.google_storage_bucket.bucket_load_test_results.name
    _CB_REGION                     = var.cb_region
    _REGION                        = var.region
    _ORG                           = var.my_org
    _SERVICE_NAME                  = var.service_name
    _ARTIFACT_REPO_NAME            = var.artifact_repo_name
    _MAX_INSTANCES                 = "1"
    _LOG_LEVEL                     = var.log_level
    _AUTH_REQUIRED                 = "True"
    _RATE_LIMIT                    = "120"    
  }

  depends_on = [
    resource.google_project_service.cicd_services, 
    resource.google_project_service.deploy_project_services, 
    google_cloudbuildv2_connection.github_connection, 
    google_cloudbuildv2_repository.repo
  ]

}

# c. Create Deploy to production trigger
resource "google_cloudbuild_trigger" "deploy_to_prod_pipeline" {
  name            = "deploy-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.cb_region
  description     = "Trigger for deployment to production"
  service_account = resource.google_service_account.cicd_runner_sa.id
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.cb_region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
  }
  filename = ".cloudbuild/deploy-to-prod.yaml"
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  approval_config {
    approval_required = true
  }
  substitutions = {
    _PROD_PROJECT_ID             = var.prod_project_id
    # Use the region for the Cloud Run service, not the build trigger
    _REGION                      = var.region
    _ARTIFACT_REPO_NAME          = var.artifact_repo_name
    _SERVICE_NAME                = var.service_name
    _LOG_LEVEL                   = var.log_level
    _AUTH_REQUIRED               = "True"
    _RATE_LIMIT                  = "120"
    _MAX_INSTANCES               = "1"
  }
  depends_on = [
    resource.google_project_service.cicd_services, 
    resource.google_project_service.deploy_project_services, 
    google_cloudbuildv2_connection.github_connection, 
    google_cloudbuildv2_repository.repo
  ]

}
