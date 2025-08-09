# # VPC Network for AlloyDB
resource "google_compute_network" "default" {
  name                    = "${var.project_name}-alloydb-network"
  project                 = var.dev_project_id
  auto_create_subnetworks = false
  depends_on = [resource.google_project_service.services]
}

# # Subnet for AlloyDB
resource "google_compute_subnetwork" "default" {
  name          = "${var.project_name}-alloydb-network"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.default.id
  project       = var.dev_project_id

  # This is required for Cloud Run VPC connectors
  purpose       = "PRIVATE"

  private_ip_google_access = true
}

# # Private IP allocation for AlloyDB
# resource "google_compute_global_address" "private_ip_alloc" {
#   name          = "${var.project_name}-private-ip"
#   project       = var.dev_project_id
#   address_type  = "INTERNAL"
#   purpose       = "VPC_PEERING"
#   prefix_length = 16
#   network       = google_compute_network.default.id

#   depends_on = [resource.google_project_service.services]
# }

# # VPC connection for AlloyDB
# resource "google_service_networking_connection" "vpc_connection" {
#   network                 = google_compute_network.default.id
#   service                 = "servicenetworking.googleapis.com"
#   reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
# }

# # AlloyDB Cluster
# resource "google_alloydb_cluster" "session_db_cluster" {
#   project         = var.dev_project_id
#   cluster_id      = "${var.project_name}-alloydb-cluster"
#   location        = var.region
#   deletion_policy = "FORCE"

#   network_config {
#     network = google_compute_network.default.id
#   }

#   depends_on = [
#     google_service_networking_connection.vpc_connection
#   ]
# }

# # AlloyDB Instance
# resource "google_alloydb_instance" "session_db_instance" {
#   cluster       = google_alloydb_cluster.session_db_cluster.name
#   instance_id   = "${var.project_name}-alloydb-instance"
#   instance_type = "PRIMARY"

#   availability_type = "REGIONAL" # Regional redundancy

#   machine_config {
#     cpu_count = 2
#   }
# }

# # Generate a random password for the database user
# resource "random_password" "db_password" {
#   length           = 16
#   special          = true
#   override_special = "!#$%&*()-_=+[]{}<>:?"
# }

# # Store the password in Secret Manager
# resource "google_secret_manager_secret" "db_password" {
#   project   = var.dev_project_id
#   secret_id = "${var.project_name}-db-password"

#   replication {
#     auto {}
#   }

#   depends_on = [resource.google_project_service.services]
# }

# resource "google_secret_manager_secret_version" "db_password" {
#   secret      = google_secret_manager_secret.db_password.id
#   secret_data = random_password.db_password.result
# }

# resource "google_alloydb_user" "db_user" {
#   cluster        = google_alloydb_cluster.session_db_cluster.name
#   user_id        = "postgres"
#   user_type      = "ALLOYDB_BUILT_IN"
#   password       = random_password.db_password.result
#   database_roles = ["alloydbsuperuser"]

#   depends_on = [google_alloydb_instance.session_db_instance]
# }
