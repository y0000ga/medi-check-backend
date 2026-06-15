#!/usr/bin/env bash

set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Usage:
#   bash infrastructure/bootstrap-gcp.sh OWNER/REPOSITORY
#
# Example:
#   bash infrastructure/bootstrap-gcp.sh awshinlearn/medi-check
# -----------------------------------------------------------------------------

GITHUB_REPOSITORY="$(
  git remote get-url origin |
  sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##'
)"

if [[ -z "${GITHUB_REPOSITORY}" ]]; then
  echo "Usage: $0 OWNER/REPOSITORY"
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: gcloud CLI is not installed or not available in PATH."
  exit 1
fi

PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"
REGION="$(gcloud config get-value run/region 2>/dev/null)"
ACTIVE_ACCOUNT="$(gcloud auth list \
  --filter='status:ACTIVE' \
  --format='value(account)' \
  | head -n 1)"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: gcloud project is not configured."
  echo "Run: gcloud config set project medi-check-backend"
  exit 1
fi

if [[ -z "${REGION}" || "${REGION}" == "(unset)" ]]; then
  echo "ERROR: Cloud Run region is not configured."
  echo "Run: gcloud config set run/region asia-east1"
  exit 1
fi

if [[ -z "${ACTIVE_ACCOUNT}" ]]; then
  echo "ERROR: No active gcloud account."
  echo "Run: gcloud auth login"
  exit 1
fi

# -----------------------------------------------------------------------------
# Non-sensitive resource names
# -----------------------------------------------------------------------------

GAR_REPOSITORY="medi-check"
IMAGE_NAME="medi-check-backend"
CLOUD_RUN_SERVICE="medi-check-backend"

CLOUD_SQL_INSTANCE="medi-check-db"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}"

DEPLOY_SA_NAME="github-deployer"
RUNTIME_SA_NAME="medi-check-runtime"

DEPLOY_SA_EMAIL="${DEPLOY_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

WIF_POOL_ID="github"
WIF_PROVIDER_ID="medi-check-main"

SECRET_NAMES=(
  "DATABASE_URL"
  "SECRET_KEY"
  "JWT_SECRET_KEY"
  "JWT_ACCESS_SECRET_KEY"
  "JWT_REFRESH_SECRET_KEY"
)

echo "============================================================"
echo "GCP bootstrap configuration"
echo "============================================================"
echo "Active account:               ${ACTIVE_ACCOUNT}"
echo "Project ID:                   ${PROJECT_ID}"
echo "Region:                       ${REGION}"
echo "GitHub repository:            ${GITHUB_REPOSITORY}"
echo "Artifact Registry repository: ${GAR_REPOSITORY}"
echo "Cloud Run service:            ${CLOUD_RUN_SERVICE}"
echo "Cloud SQL connection:         ${CLOUD_SQL_CONNECTION_NAME}"
echo "Deploy service account:       ${DEPLOY_SA_EMAIL}"
echo "Runtime service account:      ${RUNTIME_SA_EMAIL}"
echo "============================================================"

# -----------------------------------------------------------------------------
# 1. Confirm project
# -----------------------------------------------------------------------------

gcloud projects describe "${PROJECT_ID}" >/dev/null

PROJECT_NUMBER="$(
  gcloud projects describe "${PROJECT_ID}" \
    --format='value(projectNumber)'
)"

# -----------------------------------------------------------------------------
# 2. Enable required APIs
# -----------------------------------------------------------------------------

echo "Enabling required Google Cloud APIs..."

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project="${PROJECT_ID}"

# -----------------------------------------------------------------------------
# 3. Create Artifact Registry repository if missing
# -----------------------------------------------------------------------------

if gcloud artifacts repositories describe "${GAR_REPOSITORY}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  >/dev/null 2>&1; then

  echo "Artifact Registry repository already exists: ${GAR_REPOSITORY}"
else
  echo "Creating Artifact Registry repository: ${GAR_REPOSITORY}"

  gcloud artifacts repositories create "${GAR_REPOSITORY}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --repository-format="docker" \
    --description="Medi Check container images"
fi

# -----------------------------------------------------------------------------
# 4. Create service accounts if missing
# -----------------------------------------------------------------------------

if gcloud iam service-accounts describe "${DEPLOY_SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  >/dev/null 2>&1; then

  echo "Deploy service account already exists: ${DEPLOY_SA_EMAIL}"
else
  echo "Creating deploy service account: ${DEPLOY_SA_EMAIL}"

  gcloud iam service-accounts create "${DEPLOY_SA_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="GitHub Actions Cloud Run Deployer"
fi

if gcloud iam service-accounts describe "${RUNTIME_SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  >/dev/null 2>&1; then

  echo "Runtime service account already exists: ${RUNTIME_SA_EMAIL}"
else
  echo "Creating runtime service account: ${RUNTIME_SA_EMAIL}"

  gcloud iam service-accounts create "${RUNTIME_SA_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="Medi Check Cloud Run Runtime"
fi

# -----------------------------------------------------------------------------
# 5. Runtime service account permissions
# -----------------------------------------------------------------------------

echo "Granting Cloud SQL Client to runtime service account..."

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
  --role="roles/cloudsql.client" \
  --condition=None \
  --quiet

echo "Checking required Secret Manager secrets..."

MISSING_SECRETS=()

for SECRET_NAME in "${SECRET_NAMES[@]}"; do
  if ! gcloud secrets describe "${SECRET_NAME}" \
    --project="${PROJECT_ID}" \
    >/dev/null 2>&1; then

    MISSING_SECRETS+=("${SECRET_NAME}")
  fi
done

if (( ${#MISSING_SECRETS[@]} > 0 )); then
  echo "ERROR: The following Secret Manager secrets do not exist:"

  for SECRET_NAME in "${MISSING_SECRETS[@]}"; do
    echo "  - ${SECRET_NAME}"
  done

  echo "Create these secrets in GCP Secret Manager, then rerun this script."
  exit 1
fi

echo "Granting Secret Manager access to runtime service account..."

for SECRET_NAME in "${SECRET_NAMES[@]}"; do
  gcloud secrets add-iam-policy-binding "${SECRET_NAME}" \
    --project="${PROJECT_ID}" \
    --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None \
    --quiet
done

# -----------------------------------------------------------------------------
# 6. Deploy service account permissions
# -----------------------------------------------------------------------------

echo "Granting Cloud Run Admin to deploy service account..."

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/run.admin" \
  --condition=None \
  --quiet

echo "Granting Artifact Registry Writer on repository..."

gcloud artifacts repositories add-iam-policy-binding "${GAR_REPOSITORY}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/artifactregistry.writer" \
  --condition=None \
  --quiet

echo "Allowing deploy service account to use runtime service account..."

gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None \
  --quiet

# -----------------------------------------------------------------------------
# 7. Workload Identity Pool
# -----------------------------------------------------------------------------

if gcloud iam workload-identity-pools describe "${WIF_POOL_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  >/dev/null 2>&1; then

  echo "Workload Identity Pool already exists: ${WIF_POOL_ID}"
else
  echo "Creating Workload Identity Pool: ${WIF_POOL_ID}"

  gcloud iam workload-identity-pools create "${WIF_POOL_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool"
fi

# -----------------------------------------------------------------------------
# 8. GitHub OIDC provider
# -----------------------------------------------------------------------------

ATTRIBUTE_MAPPING="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref"
ATTRIBUTE_CONDITION="assertion.repository == '${GITHUB_REPOSITORY}' && assertion.ref == 'refs/heads/main'"

if gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${WIF_POOL_ID}" \
  >/dev/null 2>&1; then

  echo "Updating Workload Identity Provider: ${WIF_PROVIDER_ID}"

  gcloud iam workload-identity-pools providers update-oidc "${WIF_PROVIDER_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${WIF_POOL_ID}" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="${ATTRIBUTE_MAPPING}" \
    --attribute-condition="${ATTRIBUTE_CONDITION}"
else
  echo "Creating Workload Identity Provider: ${WIF_PROVIDER_ID}"

  gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${WIF_POOL_ID}" \
    --display-name="Medi Check main deployment" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="${ATTRIBUTE_MAPPING}" \
    --attribute-condition="${ATTRIBUTE_CONDITION}"
fi

WIF_POOL_NAME="$(
  gcloud iam workload-identity-pools describe "${WIF_POOL_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --format='value(name)'
)"

WIF_PROVIDER_NAME="$(
  gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER_ID}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="${WIF_POOL_ID}" \
    --format='value(name)'
)"

# -----------------------------------------------------------------------------
# 9. Allow GitHub repository to impersonate deploy service account
# -----------------------------------------------------------------------------

echo "Granting GitHub repository permission to impersonate deploy SA..."

gcloud iam service-accounts add-iam-policy-binding "${DEPLOY_SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --member="principalSet://iam.googleapis.com/${WIF_POOL_NAME}/attribute.repository/${GITHUB_REPOSITORY}" \
  --role="roles/iam.workloadIdentityUser" \
  --condition=None \
  --quiet

# -----------------------------------------------------------------------------
# 10. Print persistent values for GitHub settings
# -----------------------------------------------------------------------------

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${GAR_REPOSITORY}/${IMAGE_NAME}"

echo
echo "============================================================"
echo "Bootstrap completed"
echo "============================================================"
echo
echo "GitHub Secrets:"
echo
echo "GCP_WORKLOAD_IDENTITY_PROVIDER=${WIF_PROVIDER_NAME}"
echo "GCP_SERVICE_ACCOUNT_EMAIL=${DEPLOY_SA_EMAIL}"
echo
echo "GitHub Variables:"
echo
echo "GCP_PROJECT_ID=${PROJECT_ID}"
echo "GCP_REGION=${REGION}"
echo "GAR_REPOSITORY=${GAR_REPOSITORY}"
echo "GAR_IMAGE=${IMAGE_NAME}"
echo "CLOUD_RUN_SERVICE=${CLOUD_RUN_SERVICE}"
echo "CLOUD_RUN_RUNTIME_SERVICE_ACCOUNT=${RUNTIME_SA_EMAIL}"
echo "CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_CONNECTION_NAME}"
echo "ENVIRONMENT=production"
echo "SQL_ECHO=false"
echo
echo "Computed image URI:"
echo "${IMAGE_URI}"
echo
echo "Project number:"
echo "${PROJECT_NUMBER}"
echo "============================================================"