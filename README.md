# Rickbot-ADK

A multi-personality chatbot build using Google Gemini, the Agent Development Kit (ADK) and the Google Agent-Starter-Pack.

## Notes

```bash
source .env
gcloud auth login --update-adc
export STAGING_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_STAGING_PROJECT --format="value(projectNumber)")
export PROD_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PRD_PROJECT --format="value(projectNumber)")

uv sync
```

## One-Time Project Setup Dev

```bash
### Pre-Reqs - projects have been created in Google Cloud and billing acccount attached
### Run from project's root folder

# Make sure we're on the Dev project...
gcloud config set project $GOOGLE_CLOUD_STAGING_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_STAGING_PROJECT
gcloud config list project

# Enable APIs
gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  storage-component.googleapis.com \
  aiplatform.googleapis.com \
  iap.googleapis.com

# Make sure we're on the Prod/CICD project...
gcloud config set project $GOOGLE_CLOUD_PRD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PRD_PROJECT
gcloud config list project

gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PRD_PROJECT \
    --member="serviceAccount:service-$PROD_PROJECT_NUMBER@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

```