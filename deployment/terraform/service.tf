# Manages creation of Cloud Run services and associated domain mappings.
# Note: initial creation is done by TF, but subsequent Cloud Run service deployment is handled by CI/CD.
# If we want to redeploy Cloud Run from this TF again, we should comment out the lifecycle blocks.

# Get project information to access the project number
data "google_project" "project" {
  for_each = local.deploy_project_ids
  project_id = local.deploy_project_ids[each.key]
}

resource "google_cloud_run_v2_service" "app_staging" {  
  name                = var.project_name
  location            = var.region
  project             = var.staging_project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    dynamic "containers" {
      for_each = local.containers
      content {
        name  = containers.value.name
        image = containers.value.image

        dynamic "ports" {
          for_each = containers.value.ports
          content {
            container_port = ports.value
          }
        }

        dynamic "env" {
          for_each = containers.value.env
          content {
            name  = env.value.name
            value = env.value.value
          }
        }

        resources {


          startup_cpu_boost = true
        }
      }
    }

    service_account = google_service_account.app_sa["staging"].email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    session_affinity = true
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # This lifecycle block prevents Terraform from overwriting the Cloud Run service when it's
  # updated by Cloud Run deployments outside of Terraform (e.g., via CI/CD pipelines)
  lifecycle {
    ignore_changes = all
  }

  # Make dependencies conditional to avoid errors.
  depends_on = [google_project_service.deploy_project_services]
}

# Create domain mappings for all listed domains
resource "google_cloud_run_domain_mapping" "app_staging_domain_mapping" {
  for_each = toset(var.staging_app_domain_name)
  name     = each.key
  project  = var.staging_project_id
  location = google_cloud_run_v2_service.app_staging.location
  metadata {
    namespace = data.google_project.project["staging"].project_id
  }
  spec {
    route_name = google_cloud_run_v2_service.app_staging.name
  }
}

resource "google_cloud_run_v2_service" "app_prod" {  
  name                = var.project_name
  location            = var.region
  project             = var.prod_project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    dynamic "containers" {
      for_each = local.containers
      content {
        name  = containers.value.name
        image = containers.value.image

        dynamic "ports" {
          for_each = containers.value.ports
          content {
            container_port = ports.value
          }
        }

        resources {
          limits = containers.value.resources.limits
          startup_cpu_boost = true
        }
      }
    }

    service_account = google_service_account.app_sa["prod"].email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    session_affinity = true
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # This lifecycle block prevents Terraform from overwriting the Cloud Run service when it's
  # updated by Cloud Run deployments outside of Terraform (e.g., via CI/CD pipelines)
  lifecycle {
    ignore_changes = all
  }

  # Make dependencies conditional to avoid errors.
  depends_on = [google_project_service.deploy_project_services]
}

# Create domain mappings for all listed domains
resource "google_cloud_run_domain_mapping" "app_prod_domain_mapping" {
  for_each = toset(var.prod_app_domain_name)
  name     = each.key
  project  = var.prod_project_id  
  location = google_cloud_run_v2_service.app_prod.location
  metadata {
    namespace = data.google_project.project["prod"].project_id
  }
  spec {
    route_name = google_cloud_run_v2_service.app_prod.name
  }
}