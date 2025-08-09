terraform {
  backend "gcs" {
    bucket = "rickbot-adk-prd-terraform-state"
    prefix = "rickbot-adk/dev"
  }
}
