locals {
  cicd_services = [
    "cloudbuild.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "iap.googleapis.com"
  ]

  deploy_project_services = [
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "iap.googleapis.com",
    "cloudtrace.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "secretmanager.googleapis.com",
    "dns.googleapis.com"
  ]

  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]

  included_files = [
    "src/**",
    "deployment/**",
    "uv.lock",
    "Dockerfile*",
    "pyproject.toml",
    "docker-compose.yml"
  ]

  # Configuration for containers based on UI type
  # Note: These are placeholders used for initial service creation.
  # CI/CD handles the actual image deployment.
  # Configuration for containers based on UI type
  # Note: These are placeholders used for initial service creation.
  # CI/CD handles the actual image deployment.
  # We define a map of containers keyed by environment (prod, staging) to handle dynamic values.
  
  # Environments configuration map
  environments = {
    staging = {
      project_id  = var.staging_project_id
      domain_name = var.staging_app_domain_name[0]
    }
    prod = {
      project_id  = var.prod_project_id
      domain_name = var.prod_app_domain_name[0]
    }
  }

  # Dynamic container configuration
  container_config = {
    for env, config in local.environments : env => var.ui_type == "react" ? [
      {
        name  = "ingress"
        image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder
        ports = [3000]
        resources = {
          limits = {
            cpu    = "0.2"
            memory = "512Mi"
          }
        }
        env = [
          { name = "NEXT_PUBLIC_API_URL", value = "http://localhost:8000" }, # Sidecar Architecture uses localhost
          { name = "NEXTAUTH_URL", value = "https://${config.domain_name}" }
        ]
      },
      {
        name  = "api-sidecar"
        image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder
        ports = [8000]
        resources = {
          limits = {
            cpu    = "0.8"
            memory = "1536Mi"
          }
        }
        env = [
          { name = "GOOGLE_CLOUD_PROJECT", value = config.project_id },
          { name = "AGENT_NAME", value = var.agent_name }
        ]
      }
    ] : [
      {
        name  = "streamlit"
        image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder
        ports = [8080]
        resources = {
          limits = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
        env = [
          { name = "GOOGLE_CLOUD_PROJECT", value = config.project_id },
          { name = "AGENT_NAME", value = var.agent_name }
        ]
      }
    ]
  }

}

