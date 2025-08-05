# Rickbot-ADK

A multi-personality chatbot build using Google Gemini, the Agent Development Kit (ADK) and the Google Agent-Starter-Pack.

## Using Agent Starter Kit

### Pre-Reqs

- Dev and Prod GCP projects created and attached to a billing account.
- Your user is the owner of both projects.

### Before Creating Project with Agent Starter Kit

```bash
# Authenticate and update ADC
# Your user needs to be the owner of both projects
gcloud auth login --update-adc

export GOOGLE_CLOUD_STAGING_PROJECT="your-dev-project"
export GOOGLE_CLOUD_PRD_PROJECT="your-prod-project"

# Make sure we're on the Dev / Staging project...
export GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_STAGING_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config list project

# Now let's enable some Google Cloud APIs in the project
gcloud services enable \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  storage-component.googleapis.com \
  aiplatform.googleapis.com
```

### Create Project with Agent Starter Kit

```bash
# Dependency is Python and uv already installed
uvx agent-starter-pack create rickbot-adk
```

### After Creating Project with Agent Starter Kit

- Update `pyproject.toml`.
- Create `.env`.

### Creating CI/CD Pipeline

First, one-time setup for Prod project. (To workaround issues I found with the `setup-cicd` command.)

```bash
# Make sure we're on the Prod/CICD project...
export GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PRD_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
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

Now we can run `setup-cicd`:

```bash
uvx agent-starter-pack setup-cicd \
  --staging-project $GOOGLE_CLOUD_STAGING_PROJECT \
  --prod-project $GOOGLE_CLOUD_PRD_PROJECT \
  --repository-name $REPO \
  --region $GOOGLE_CLOUD_BUILD_REGION # I have no quota to run Cloud Build in my preferred region
```

The following is just for my own quota issue. May not apply to others! Update the following to split out REGION and CB_REGION:

- staging.yaml
- build_triggers.tf
- github.tf
- variables.tf
- env.tfvars (x2)

## Per Dev Session

```bash
# From rickbot-adk project folder
source .env

gcloud auth login --update-adc
export STAGING_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_STAGING_PROJECT --format="value(projectNumber)")
export PROD_PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PRD_PROJECT --format="value(projectNumber)")

uv sync --dev --extra jupyter # Or we can use make install, from Agent Starter Kit
source .venv/bin/activate
```

## Deploying Infra Commands

If we need to redeploy...

```bash
# Assuming we're in the project root folder
cd deployment/terraform
terraform init # One time initialisation

# Create the TF plan
terraform plan -var-file="vars/env.tfvars" -out out.tfplan

# Check the TF plan then apply
terraform apply "out.tfplan"
```

## ADK

### Testing Locally

With CLI:

```bash
uv run adk run app
```

With GUI:

```bash
uv run adk web

# Or we can use the Agent Starter Git make aliases
make install && make playground
```

### Testing Remote

Use the `adk_app_testing.ipynb` notebook.