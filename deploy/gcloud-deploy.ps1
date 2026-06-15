$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [Parameter(Mandatory = $true)]
    [string]$Region,

    [Parameter(Mandatory = $true)]
    [string]$ServiceName,

    [Parameter(Mandatory = $true)]
    [string]$ImageUri,

    [Parameter(Mandatory = $true)]
    [string]$CloudSqlInstanceConnectionName,

    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrlSecret,

    [Parameter(Mandatory = $true)]
    [string]$SecretKeySecret,

    [Parameter(Mandatory = $true)]
    [string]$JwtSecretKeySecret,

    [Parameter(Mandatory = $true)]
    [string]$JwtAccessSecretKeySecret,

    [Parameter(Mandatory = $true)]
    [string]$JwtRefreshSecretKeySecret,

    [string]$CorsOrigins = "",
    [string]$Environment = "production"
)

Write-Host "Setting gcloud project to $ProjectId"
gcloud config set project $ProjectId

Write-Host "Deploying to Cloud Run using image $ImageUri"
gcloud run deploy $ServiceName `
    --image $ImageUri `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --add-cloudsql-instances $CloudSqlInstanceConnectionName `
    --set-env-vars "ENVIRONMENT=$Environment,CORS_ORIGINS=$CorsOrigins,SQL_ECHO=false" `
    --set-secrets "DATABASE_URL=$DatabaseUrlSecret,SECRET_KEY=$SecretKeySecret,JWT_SECRET_KEY=$JwtSecretKeySecret,JWT_ACCESS_SECRET_KEY=$JwtAccessSecretKeySecret,JWT_REFRESH_SECRET_KEY=$JwtRefreshSecretKeySecret"
