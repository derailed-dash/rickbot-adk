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
