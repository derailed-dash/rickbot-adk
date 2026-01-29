#!/usr/bin/env bash
set -e

# Define common environment variables
export COMMON_ENV_VARS="
- name: GOOGLE_CLOUD_PROJECT
  value: \"$_PROD_PROJECT_ID\"
- name: GOOGLE_CLOUD_REGION
  value: \"$_REGION\"
- name: LOG_LEVEL
  value: \"$_LOG_LEVEL\"
- name: APP_NAME
  value: \"$_APP_NAME\"
- name: AGENT_NAME
  value: \"$_AGENT_NAME\"
- name: GOOGLE_GENAI_USE_VERTEXAI
  value: \"$_GOOGLE_GENAI_USE_VERTEXAI\"
- name: MODEL
  value: \"$_MODEL\"
- name: AUTH_REQUIRED
  value: \"$_AUTH_REQUIRED\"
- name: RATE_LIMIT
  value: \"$_RATE_LIMIT\"
- name: GOOGLE_CLOUD_LOCATION
  value: \"$_GOOGLE_CLOUD_LOCATION\"
"

# Define common environment variables (Flags format for Streamlit)
export COMMON_ENV_FLAGS="GOOGLE_CLOUD_PROJECT=$_PROD_PROJECT_ID,"
COMMON_ENV_FLAGS+="GOOGLE_CLOUD_REGION=$_REGION,"
COMMON_ENV_FLAGS+="LOG_LEVEL=$_LOG_LEVEL,"
COMMON_ENV_FLAGS+="APP_NAME=$_APP_NAME,"
COMMON_ENV_FLAGS+="AGENT_NAME=$_AGENT_NAME,"
COMMON_ENV_FLAGS+="GOOGLE_GENAI_USE_VERTEXAI=$_GOOGLE_GENAI_USE_VERTEXAI,"
COMMON_ENV_FLAGS+="MODEL=$_MODEL,"
COMMON_ENV_FLAGS+="AUTH_REQUIRED=$_AUTH_REQUIRED,"
COMMON_ENV_FLAGS+="RATE_LIMIT=$_RATE_LIMIT,"
COMMON_ENV_FLAGS+="GOOGLE_CLOUD_LOCATION=$_GOOGLE_CLOUD_LOCATION"

if [ "$_UI_TYPE" = "react" ]; then
  echo "Deploying React Sidecar architecture to Production..."
  
  cat <<EOF > service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: $_SERVICE_NAME
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/launch-stage: BETA
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/startup-cpu-boost: 'true'
    spec:
      serviceAccountName: $_SERVICE_NAME-app-sa@$_PROD_PROJECT_ID.iam.gserviceaccount.com
      containers:
      - name: ingress
        image: $_REGION-docker.pkg.dev/$PROJECT_ID/$_ARTIFACT_REPO_NAME/$_SERVICE_NAME-react-fe:$SHORT_SHA
        ports:
        - containerPort: 3000
        resources:
          limits:
            cpu: '0.2'
            memory: 512Mi
        env:
        - name: NEXT_PUBLIC_API_URL
          value: http://localhost:8000
        - name: NEXTAUTH_URL
          value: $_APP_URL
      - name: api-sidecar
        image: $_REGION-docker.pkg.dev/$PROJECT_ID/$_ARTIFACT_REPO_NAME/$_SERVICE_NAME-api-sidecar:$SHORT_SHA
        resources:
          limits:
            cpu: '0.8'
            memory: 1536Mi
        env:
$COMMON_ENV_VARS
EOF

  gcloud beta run services replace service.yaml --project="$_PROD_PROJECT_ID" --region="$_REGION"
  
  # Explicitly allow unauthenticated access (public) as 'replace' might reset/ignore it
  gcloud run services add-iam-policy-binding "$_SERVICE_NAME" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --region="$_REGION" \
    --project="$_PROD_PROJECT_ID"
else
  echo "Deploying Streamlit (Legacy) architecture to Production..."
  gcloud run deploy "$_SERVICE_NAME" \
    --image="$_REGION-docker.pkg.dev/$PROJECT_ID/$_ARTIFACT_REPO_NAME/$_SERVICE_NAME-streamlit:$SHORT_SHA" \
    --region="$_REGION" \
    --project="$_PROD_PROJECT_ID" \
    --max-instances=$_MAX_INSTANCES \
    --cpu-boost \
    --set-env-vars="$COMMON_ENV_FLAGS" \
    --service-account="$_SERVICE_NAME-app-sa@$_PROD_PROJECT_ID.iam.gserviceaccount.com" \
    --allow-unauthenticated
fi
