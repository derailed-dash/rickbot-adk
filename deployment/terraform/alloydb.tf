# VPC Network for AlloyDB
# resource "google_compute_network" "default" {
#   for_each = local.deploy_project_ids
  
#   name                    = "${var.project_name}-alloydb-network"
#   project                 = local.deploy_project_ids[each.key]
#   auto_create_subnetworks = false
  
#   depends_on = [google_project_service.deploy_project_services]
# }

# Subnet for AlloyDB
# resource "google_compute_subnetwork" "default" {
#   for_each = local.deploy_project_ids
  
#   name          = "${var.project_name}-alloydb-network"
#   ip_cidr_range = "10.0.0.0/24"
#   region        = var.region
#   network       = google_compute_network.default[each.key].id
#   project       = local.deploy_project_ids[each.key]

#   # This is required for Cloud Run VPC connectors
#   purpose       = "PRIVATE"

#   private_ip_google_access = true
# }

# Private IP allocation for AlloyDB
# resource "google_compute_global_address" "private_ip_alloc" {
#   for_each = local.deploy_project_ids
  
#   name          = "${var.project_name}-private-ip"
#   project       = local.deploy_project_ids[each.key]
#   address_type  = "INTERNAL"
#   purpose       = "VPC_PEERING"
#   prefix_length = 16
#   network       = google_compute_network.default[each.key].id

#   depends_on = [google_project_service.deploy_project_services]
# }

# VPC connection for AlloyDB
# resource "google_service_networking_connection" "vpc_connection" {
#   for_each = local.deploy_project_ids
  
#   network                 = google_compute_network.default[each.key].id
#   service                 = "servicenetworking.googleapis.com"
#   reserved_peering_ranges = [google_compute_global_address.private_ip_alloc[each.key].name]
# }

# AlloyDB Cluster
# resource "google_alloydb_cluster" "session_db_cluster" {
#   for_each = local.deploy_project_ids
  
#   project         = local.deploy_project_ids[each.key]
#   cluster_id      = "${var.project_name}-alloydb-cluster"
#   location        = var.region
#   deletion_policy = "FORCE"

#   network_config {
#     network = google_compute_network.default[each.key].id
#   }

#   depends_on = [
#     google_service_networking_connection.vpc_connection
#   ]
# }

# AlloyDB Instance
# resource "google_alloydb_instance" "session_db_instance" {
#   for_each = local.deploy_project_ids
  
#   cluster       = google_alloydb_cluster.session_db_cluster[each.key].name
#   instance_id   = "${var.project_name}-alloydb-instance"
#   instance_type = "PRIMARY"

#   availability_type = "REGIONAL" # Regional redundancy

#   machine_config {
#     cpu_count = 2
#   }
# }

# Generate a random password for the database user
# resource "random_password" "db_password" {
#   for_each = local.deploy_project_ids
  
#   length           = 16
#   special          = true
#   override_special = "!#$%&*()-_=+[]{}<>:?"
# }

# Store the password in Secret Manager
# resource "google_secret_manager_secret" "db_password" {
#   for_each = local.deploy_project_ids
  
#   project   = local.deploy_project_ids[each.key]
#   secret_id = "${var.project_name}-db-password"

#   replication {
#     auto {}
#   }

#   depends_on = [google_project_service.deploy_project_services]
# }

# resource "google_secret_manager_secret_version" "db_password" {
#   for_each = local.deploy_project_ids
  
#   secret      = google_secret_manager_secret.db_password[each.key].id
#   secret_data = random_password.db_password[each.key].result
# }

# resource "google_alloydb_user" "db_user" {
#   for_each = local.deploy_project_ids
  
#   cluster        = google_alloydb_cluster.session_db_cluster[each.key].name
#   user_id        = "postgres"
#   user_type      = "ALLOYDB_BUILT_IN"
#   password       = random_password.db_password[each.key].result
#   database_roles = ["alloydbsuperuser"]

#   depends_on = [google_alloydb_instance.session_db_instance]
# }
