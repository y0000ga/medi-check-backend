# Migration Workflow

This project uses Alembic to manage database schema changes for both local development and production deployments.

## Goals

- Keep the schema reproducible across environments
- Avoid manual database edits
- Make every schema change reviewable in version control
- Keep Cloud Run deployments and schema changes in sync

## How Migrations Work

- The application reads `DATABASE_URL` from settings.
- Alembic uses the same `DATABASE_URL` in `migrations/env.py`.
- Local development usually targets the bundled PostgreSQL container.
- Production targets the Cloud SQL PostgreSQL instance.

## Initial Setup

When the project needs a brand-new migration history:

1. Make sure all SQLAlchemy models are imported in `migrations/env.py`
2. Confirm `Base.metadata` includes every table you want Alembic to track
3. Generate the first revision:

```powershell
uv run alembic revision --autogenerate -m "initial schema"
```

4. Review the generated migration carefully
5. Apply it to the target database:

```powershell
uv run alembic upgrade head
```

The initial migration should create the full schema from scratch.

## Standard Change Flow

For any later schema change, follow this flow:

1. Change the SQLAlchemy model first
2. Update repository or service code if the new schema changes behavior
3. Generate a new revision:

```powershell
uv run alembic revision --autogenerate -m "describe the change"
```

4. Inspect the generated migration file
5. Edit the migration if Alembic missed anything or generated something unsafe
6. Run the migration locally:

```powershell
uv run alembic upgrade head
```

7. Test the affected API flow
8. Commit the model change and migration together

## Before Deploying to Cloud Run

When a schema change is part of a release:

1. Build and push the new image
2. Run Alembic against the Cloud SQL database
3. Confirm the migration is successful
4. Release the new Cloud Run revision

Do not rely on Cloud Run startup to apply migrations automatically.

## Production Migration Sequence

A safe production sequence looks like this:

```powershell
uv run alembic current
uv run alembic upgrade head
```

If the schema change is risky, back up the database before applying the migration.

## What to Review in Every Migration

- Table and column names
- Nullable and non-nullable changes
- Default values
- Foreign keys
- Unique constraints
- Indexes
- Enum changes
- Data migration safety

## Rules of Thumb

- Do not edit the database manually if the change belongs in Alembic
- Do not skip reviewing autogenerate output
- Keep model changes and migration files in the same pull request
- If a migration needs data backfill, keep the operation explicit and reversible when possible
- Keep migrations compatible with the Cloud SQL instance used by Cloud Run

## Local Development

When working locally:

1. Start PostgreSQL
2. Apply migrations before running the app
3. If the schema changed, regenerate and apply the new revision
4. Refresh pgAdmin after the migration finishes if you are viewing the database there

Recommended commands:

```powershell
docker compose up -d postgres
uv run alembic upgrade head
uv run python -m app
```

If tables do not appear in pgAdmin, verify that it is connected to the same database as `.env`:

- Host: `localhost`
- Port: `5432`
- Database: `medi_check`
- Username: `medi_check_user`
- Password: `medi_check_password`

Then expand `Databases > medi_check > Schemas > public > Tables` and refresh the tree.

## Cloud SQL Deployment Notes

- Use the Cloud SQL PostgreSQL instance as the production migration target.
- Keep `DATABASE_URL` in Secret Manager or another secure secret store.
- Run migrations before exposing a new Cloud Run revision to real traffic if the schema changed.

## Troubleshooting

- If Alembic says there is no current revision, the database may be empty or the version table may not exist yet
- If `autogenerate` produces an unexpected diff, check whether all models are imported in `migrations/env.py`
- If a migration fails, fix the migration file first instead of editing the database manually
- If pgAdmin does not show newly created tables, confirm the migration finished successfully and refresh the browser tree
- If Cloud Run starts but the app cannot read data, confirm the Cloud SQL instance and `DATABASE_URL` both point to the same database
