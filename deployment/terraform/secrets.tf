# Create secrets in Secret Manager.
# Does NOT create any values

resource "google_secret_manager_secret" "dazbo_system_prompt" {
  for_each      = local.deploy_project_ids
  project       = each.value
  secret_id = "dazbo-system-prompt"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "rickbot-streamlit-secrets-toml" {
  for_each      = local.deploy_project_ids
  project       = each.value
  secret_id = "rickbot-streamlit-secrets-toml"

  replication {
    auto {}
  }
}

# This creates the secret placeholder.
# We can then populate the secret like this:
# gcloud secrets versions add google-api-key --data="<API_KEY>"
resource "google_secret_manager_secret" "google_api_key" {
  for_each = local.deploy_project_ids
  project  = each.value
  secret_id = "google-api-key"

  replication {
    auto {}
  }
}
