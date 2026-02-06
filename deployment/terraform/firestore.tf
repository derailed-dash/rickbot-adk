resource "google_firestore_database" "database" {
  for_each = local.deploy_project_ids

  project     = each.value
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  # Wait for the Firestore API to be enabled
  depends_on = [google_project_service.deploy_project_services]
}
