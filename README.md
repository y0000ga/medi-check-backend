# Medi Check Backend

Backend service for Medi Check, built with FastAPI and SQLAlchemy.

The application runs locally with PostgreSQL and is designed for deployment on Google Cloud Run with Cloud SQL.

## Overview

- Framework: FastAPI
- Database: PostgreSQL
- Migration tool: Alembic
- Runtime: Python 3.12+

## Prerequisites

- Python 3.12 or 3.13
- `uv`
- Docker Desktop for local PostgreSQL
- Google Cloud CLI for deployment

## Local Development

### 1. Create the environment file

```powershell
copy .env.example .env
```

### 2. Install dependencies

```powershell
uv sync --group dev
```

### 3. Start PostgreSQL

```powershell
docker compose up -d postgres
```

### 4. Apply migrations

```powershell
uv run alembic upgrade head
```

### 5. Start the application

```powershell
uv run python -m app
```

The API listens on port `8080`.

## API Endpoints

- API Docs: `https://y0000ga.github.io/medi-check-backend/`
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
- Health check: `http://localhost:8080/health`
- Readiness check: `http://localhost:8080/health/ready`

## Useful Commands

```powershell
uv run ruff check .
uv run pytest
docker compose ps
docker compose logs -f postgres
```

## Deployment

Production deployment uses Cloud Run for compute, Cloud SQL for PostgreSQL, Artifact Registry for container images, and Secret Manager for secrets.

### GCP resources to create

1. Enable required APIs.
   - Cloud Run
   - Artifact Registry
   - Cloud Build
   - Secret Manager
   - Cloud SQL Admin

2. Create an Artifact Registry Docker repository.
   - Suggested name: `medi-check-backend`
   - Suggested region: `asia-east1`

3. Create a Cloud SQL PostgreSQL instance.
   - Use the same region as Cloud Run when possible.
   - Example instance name: `medi-check-db`

4. Create Secret Manager secrets.
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `JWT_ACCESS_SECRET_KEY`
   - `JWT_REFRESH_SECRET_KEY`

5. Create a Cloud Run service.
   - Container port: `8080`
   - Authentication: enable unauthenticated access only if the API is public

### Initial Cloud SQL setup

Use these commands the first time you create the database:

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com sqladmin.googleapis.com
gcloud sql instances create medi-check-db --database-version=POSTGRES_16 --region=asia-east1
gcloud sql databases create medi_check --instance=medi-check-db
gcloud sql users create medi_check_user --instance=medi-check-db --password=YOUR_DB_PASSWORD
```

Recommended database connection string:

```text
postgresql+psycopg://medi_check_user:YOUR_DB_PASSWORD@/medi_check?host=/cloudsql/YOUR_PROJECT_ID:asia-east1:medi-check-db
```

### Initial Secret Manager setup

Create the secrets:

```powershell
gcloud secrets create DATABASE_URL --replication-policy="automatic"
gcloud secrets create SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_ACCESS_SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_REFRESH_SECRET_KEY --replication-policy="automatic"
```

Add secret values:

```powershell
gcloud secrets versions add DATABASE_URL --data-file=PATH_TO_DATABASE_URL.txt
gcloud secrets versions add SECRET_KEY --data-file=PATH_TO_SECRET_KEY.txt
gcloud secrets versions add JWT_SECRET_KEY --data-file=PATH_TO_JWT_SECRET_KEY.txt
gcloud secrets versions add JWT_ACCESS_SECRET_KEY --data-file=PATH_TO_JWT_ACCESS_SECRET_KEY.txt
gcloud secrets versions add JWT_REFRESH_SECRET_KEY --data-file=PATH_TO_JWT_REFRESH_SECRET_KEY.txt
```

### Cloud Run configuration

Set these environment variables on the Cloud Run service:

- `ENVIRONMENT=production`
- `CORS_ORIGINS=https://your-frontend.example.com`
- `SQL_ECHO=false`

Inject these from Secret Manager:

- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`

Attach the Cloud SQL instance using the instance connection name.

### Cloud Build Trigger

`cloudbuild.yaml` is build-only. It builds and pushes the container image to Artifact Registry, and a separate trigger or deployment step should handle Cloud Run release.

Suggested trigger flow:

1. Create a Cloud Build trigger on your main branch.
2. Point the trigger to [`cloudbuild.yaml`](cloudbuild.yaml).
3. Configure the trigger to build on push to `main`.
4. Use the resulting image tag in your deployment step.

If you want a fully automatic release, keep the build trigger and add a second deployment step in your release pipeline, or use the GitHub Actions workflow in this repository.

#### Cloud Build Trigger setup in the console

1. Open the Google Cloud Console and go to **Cloud Build**.
2. Select **Triggers** from the left menu.
3. Click **Create trigger**.
4. Choose your source provider, usually GitHub or Cloud Source Repositories.
5. Connect the repository that contains this backend.
6. Set the branch filter to `^main$` or your release branch.
7. In the build configuration section, choose **Cloud Build configuration file**.
8. Set the configuration file path to `cloudbuild.yaml`.
9. Confirm the substitutions:
   - `_REGION=asia-east1`
   - `_AR_REPO=medi-check-backend`
   - `_IMAGE=medi-check-backend`
10. Save the trigger.
11. Push a commit to the selected branch to verify that the image is built and pushed to Artifact Registry.
12. Copy the resulting image URI and pass it to the release step.

What you should see after a successful build:

- A new image tag in Artifact Registry
- A Cloud Build execution record with build and push steps only
- No Cloud Run deployment from this trigger

If you want the release to happen automatically after the build, create a separate release workflow or use the GitHub Actions release template below.

### Cloud Run deployment

Use the helper script in [`deploy/gcloud-deploy.ps1`](deploy/gcloud-deploy.ps1) for manual deployment.

Example deployment command:

```powershell
.\deploy\gcloud-deploy.ps1 `
  -ProjectId YOUR_PROJECT_ID `
  -Region asia-east1 `
  -ServiceName medi-check-backend `
  -ImageName medi-check-backend `
  -ArtifactRegistryRepo medi-check-backend `
  -CloudSqlInstanceConnectionName YOUR_PROJECT_ID:asia-east1:medi-check-db `
  -DatabaseUrlSecret DATABASE_URL:latest `
  -SecretKeySecret SECRET_KEY:latest `
  -JwtSecretKeySecret JWT_SECRET_KEY:latest `
  -JwtAccessSecretKeySecret JWT_ACCESS_SECRET_KEY:latest `
  -JwtRefreshSecretKeySecret JWT_REFRESH_SECRET_KEY:latest `
  -CorsOrigins https://your-frontend.example.com
```

### Health checks

- `GET /health` for liveness
- `GET /health/ready` for readiness and database verification

## GitHub Actions

Use [`.github/workflows/build-image.yml`](.github/workflows/build-image.yml) for image build and push.

Required GitHub configuration:

- `vars.GCP_PROJECT_ID`
- `secrets.GCP_WORKLOAD_IDENTITY_PROVIDER`
- `secrets.GCP_SERVICE_ACCOUNT_EMAIL`

The build workflow pushes the image to Artifact Registry.
The release workflow is automatic and is defined in [`.github/workflows/release-cloudrun.yml`](.github/workflows/release-cloudrun.yml).

### Release workflow template

1. Push a commit to `main`.
2. The build workflow builds and pushes the image.
3. The release workflow receives the completed build event.
4. Cloud Run deploys the image tagged with the same commit SHA.

If you need a manual release, use [`deploy/gcloud-deploy.ps1`](deploy/gcloud-deploy.ps1) with an explicit image URI.

Example image URI:

```text
asia-east1-docker.pkg.dev/YOUR_PROJECT_ID/medi-check-backend/medi-check-backend:YOUR_TAG
```

Confirm that the workflow deploys the image to Cloud Run.

## Troubleshooting

### Cloud Run starts but returns 500 on database access

- Confirm `DATABASE_URL` is stored in Secret Manager and injected into Cloud Run.
- Confirm the Cloud SQL instance is attached to the Cloud Run service.
- Confirm the instance connection name matches the actual Cloud SQL instance.
- Check whether the database user and database name exist.

### Cloud Run fails to start

- Confirm `ENVIRONMENT=production` is set only for production.
- Confirm `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_ACCESS_SECRET_KEY`, and `JWT_REFRESH_SECRET_KEY` are present.
- Confirm the service container listens on port `8080`.
- Check Cloud Run logs for import-time errors from settings or database setup.

### Cloud Build succeeds but Cloud Run is not updated

- `cloudbuild.yaml` is build-only by design.
- Build output goes to Artifact Registry only.
- Use the Cloud Run deployment script, GitHub Actions release job, or a separate deployment trigger to release the image.

### Secret Manager values are not visible in Cloud Run

- Verify the secret names match exactly.
- Verify the Cloud Run service account has `Secret Manager Secret Accessor`.
- Add a new secret version if you update a secret value.

### CORS failures in the browser

- Verify `CORS_ORIGINS` contains the exact frontend origin, including scheme and port.
- Multiple origins should be comma-separated.
- Make sure the frontend URL in production is not still pointing to localhost.

### Readiness check returns `degraded`

- Confirm the Cloud SQL instance is reachable.
- Confirm the database exists and the credentials are correct.
- Check whether the Cloud Run service has permission and network access to the database.

## Notes

- Keep `CORS_ORIGINS` aligned with your frontend domain.
- Keep all production secrets in Secret Manager.
- Run migrations before exposing the service to real traffic.
- `service.yaml` is a legacy manifest kept for reference only and is not part of the current Cloud Run deployment flow.
