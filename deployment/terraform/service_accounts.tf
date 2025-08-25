resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CICD Runner SA"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
# Agent service account
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app-sa"
  display_name = "${var.project_name} Agent Service Account"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}


