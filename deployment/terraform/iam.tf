# Data source to get project numbers
data "google_project" "projects" {
  for_each   = local.deploy_project_ids
  project_id = each.value
}

# 1. Assign roles for the CICD project
resource "google_project_iam_member" "cicd_project_roles" {
  for_each = toset(var.cicd_roles)

  project    = var.cicd_runner_project_id
  role       = each.value
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

# 2. Assign roles for the other two projects (prod and staging)
resource "google_project_iam_member" "other_projects_roles" {
  for_each = {
    for pair in setproduct(keys(local.deploy_project_ids), var.cicd_sa_deployment_required_roles) :
    "${pair[0]}-${pair[1]}" => {
      project_id = local.deploy_project_ids[pair[0]]
      role       = pair[1]
    }
  }

  project    = each.value.project_id
  role       = each.value.role
  member     = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

locals {
  # Create a flattened list of all project/role bindings for the application service accounts.
  # This makes the resource block below much easier to read and understand.
  app_sa_bindings = flatten([
    for proj_key, proj_id in local.deploy_project_ids : [
      for role in var.app_sa_roles : {
        binding_key = "${proj_key}-${role}"
        project_id  = proj_id
        project_key = proj_key
        role        = role
      }
    ]
  ])
}

# 3. Grant application SA the required permissions to run the application
resource "google_project_iam_member" "app_sa_roles" {
  for_each   = { for binding in local.app_sa_bindings : binding.binding_key => binding }
  project    = each.value.project_id
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.app_sa[each.value.project_key].email}"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}


# 4. Allow Cloud Run service SA to pull containers stored in the CICD project
resource "google_project_iam_member" "cicd_run_invoker_artifact_registry_reader" {
  for_each = local.deploy_project_ids
  project  = var.cicd_runner_project_id

  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${data.google_project.projects[each.key].number}@serverless-robot-prod.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]

}

resource "google_secret_manager_secret_iam_member" "dazbo_system_prompt_access" {
  for_each   = local.deploy_project_ids
  project    = each.value
  secret_id  = "dazbo-system-prompt"
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:service-${data.google_project.projects[each.key].number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
  depends_on = [google_secret_manager_secret.dazbo_system_prompt]
}


# Special assignment: Allow the CICD SA to create tokens
resource "google_service_account_iam_member" "cicd_run_invoker_token_creator" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
# Special assignment: Allow the CICD SA to impersonate himself for trigger creation
resource "google_service_account_iam_member" "cicd_run_invoker_account_user" {
  service_account_id = google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${resource.google_service_account.cicd_runner_sa.email}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
