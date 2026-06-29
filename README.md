# Medi Check Backend

Medi Check 後端服務，使用 FastAPI 與 SQLAlchemy 建構。

本應用程式可在本機搭配 PostgreSQL 執行，並設計為部署至 Google Cloud Run 搭配 Cloud SQL。

## 概覽

- 框架：FastAPI
- 資料庫：PostgreSQL
- Migration 工具：Alembic
- 執行環境：Python 3.12+

## 必要條件

- Python 3.12 或 3.13
- `uv`
- Docker Desktop（本機 PostgreSQL 用）
- Google Cloud CLI（部署用）

## 本機開發

### 1. 建立環境設定檔

```powershell
copy .env.example .env
```

### 2. 安裝相依套件

```powershell
uv sync --group dev
```

### 3. 啟動 PostgreSQL

```powershell
docker compose up -d postgres
```

### 4. 套用 Migration

```powershell
uv run alembic upgrade head
```

### 5. 啟動應用程式

```powershell
uv run fastapi dev app/main.py
```

API 監聽於 port `8000`。

## API 端點

- API Docs：`https://y0000ga.github.io/medi-check-backend/`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- 健康檢查：`http://localhost:8000/health`
- 就緒檢查：`http://localhost:8000/health/ready`

## 常用指令

```powershell
uv run ruff check .
uv run pytest
docker compose ps
docker compose logs -f postgres
```

## 部署

正式環境部署使用 Cloud Run 執行運算、Cloud SQL 作為 PostgreSQL、Artifact Registry 存放容器映像，以及 Secret Manager 管理機密資訊。

### 建立 GCP 資源

1. 啟用所需 API：
   - Cloud Run
   - Artifact Registry
   - Cloud Build
   - Secret Manager
   - Cloud SQL Admin

2. 建立 Artifact Registry Docker 儲存庫：
   - 建議名稱：`medi-check-backend`
   - 建議區域：`asia-east1`

3. 建立 Cloud SQL PostgreSQL 執行個體：
   - 建議使用與 Cloud Run 相同的區域
   - 執行個體名稱範例：`medi-check-db`

4. 建立 Secret Manager 機密：
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `JWT_ACCESS_SECRET_KEY`
   - `JWT_REFRESH_SECRET_KEY`

5. 建立 Cloud Run 服務：
   - 容器 port：`8080`
   - 驗證：僅在 API 公開時才啟用未驗證存取

### 初次設定 Cloud SQL

第一次建立資料庫時執行以下指令：

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com sqladmin.googleapis.com
gcloud sql instances create medi-check-db --database-version=POSTGRES_16 --region=asia-east1
gcloud sql databases create medi_check --instance=medi-check-db
gcloud sql users create medi_check_user --instance=medi-check-db --password=YOUR_DB_PASSWORD
```

建議的資料庫連線字串：

```text
postgresql+psycopg://medi_check_user:YOUR_DB_PASSWORD@/medi_check?host=/cloudsql/YOUR_PROJECT_ID:asia-east1:medi-check-db
```

### 初次設定 Secret Manager

建立機密：

```powershell
gcloud secrets create DATABASE_URL --replication-policy="automatic"
gcloud secrets create SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_ACCESS_SECRET_KEY --replication-policy="automatic"
gcloud secrets create JWT_REFRESH_SECRET_KEY --replication-policy="automatic"
```

新增機密值：

```powershell
gcloud secrets versions add DATABASE_URL --data-file=PATH_TO_DATABASE_URL.txt
gcloud secrets versions add SECRET_KEY --data-file=PATH_TO_SECRET_KEY.txt
gcloud secrets versions add JWT_SECRET_KEY --data-file=PATH_TO_JWT_SECRET_KEY.txt
gcloud secrets versions add JWT_ACCESS_SECRET_KEY --data-file=PATH_TO_JWT_ACCESS_SECRET_KEY.txt
gcloud secrets versions add JWT_REFRESH_SECRET_KEY --data-file=PATH_TO_JWT_REFRESH_SECRET_KEY.txt
```

### Cloud Run 設定

在 Cloud Run 服務上設定以下環境變數：

- `ENVIRONMENT=production`
- `CORS_ORIGINS=https://your-frontend.example.com`
- `SQL_ECHO=false`

從 Secret Manager 注入以下機密：

- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`

使用執行個體連線名稱掛載 Cloud SQL 執行個體。

### Cloud Build Trigger

`cloudbuild.yaml` 僅負責建置，會建構並推送容器映像至 Artifact Registry，Cloud Run 的發布需由獨立的 trigger 或部署步驟處理。

建議的 trigger 流程：

1. 建立指向 main 分支的 Cloud Build trigger。
2. 將 trigger 指向 [`cloudbuild.yaml`](cloudbuild.yaml)。
3. 設定在推送至 `main` 時觸發建置。
4. 將產生的映像標籤用於部署步驟。

如需完全自動化發布，保留建置 trigger 並在發布 pipeline 中新增第二個部署步驟，或使用本儲存庫中的 GitHub Actions workflow。

#### 在 Google Cloud Console 設定 Cloud Build Trigger

1. 開啟 Google Cloud Console，進入 **Cloud Build**。
2. 從左側選單選擇 **Triggers**。
3. 點擊 **Create trigger**。
4. 選擇來源提供者，通常為 GitHub 或 Cloud Source Repositories。
5. 連結包含此後端的儲存庫。
6. 設定分支過濾條件為 `^main$` 或你的發布分支。
7. 在建置設定欄位選擇 **Cloud Build configuration file**。
8. 設定設定檔路徑為 `cloudbuild.yaml`。
9. 確認替換變數：
   - `_REGION=asia-east1`
   - `_AR_REPO=medi-check-backend`
   - `_IMAGE=medi-check-backend`
10. 儲存 trigger。
11. 推送一個 commit 至選定的分支，確認映像已建置並推送至 Artifact Registry。
12. 複製產生的映像 URI，傳遞給發布步驟使用。

成功建置後應看到：

- Artifact Registry 中出現新的映像標籤
- Cloud Build 執行紀錄中只包含建置與推送步驟
- 此 trigger 不會觸發 Cloud Run 部署

如需建置後自動發布，請建立獨立的發布 workflow 或使用下方的 GitHub Actions 發布範本。

### Cloud Run 部署

使用 [`deploy/gcloud-deploy.ps1`](deploy/gcloud-deploy.ps1) 協助腳本進行手動部署。

部署指令範例：

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

### 健康檢查

- `GET /health`：存活確認（liveness）
- `GET /health/ready`：就緒確認（readiness）並驗證資料庫連線

## GitHub Actions

使用 [`.github/workflows/build-image.yml`](.github/workflows/build-image.yml) 進行映像建置與推送。

必要的 GitHub 設定：

- `vars.GCP_PROJECT_ID`
- `secrets.GCP_WORKLOAD_IDENTITY_PROVIDER`
- `secrets.GCP_SERVICE_ACCOUNT_EMAIL`

建置 workflow 會將映像推送至 Artifact Registry。
發布 workflow 為自動觸發，定義於 [`.github/workflows/release-cloudrun.yml`](.github/workflows/release-cloudrun.yml)。

### 發布流程範本

1. 推送 commit 至 `main`。
2. 建置 workflow 建構並推送映像。
3. 發布 workflow 接收到建置完成事件。
4. Cloud Run 部署以相同 commit SHA 標記的映像。

如需手動發布，使用 [`deploy/gcloud-deploy.ps1`](deploy/gcloud-deploy.ps1) 並指定明確的映像 URI。

映像 URI 範例：

```text
asia-east1-docker.pkg.dev/YOUR_PROJECT_ID/medi-check-backend/medi-check-backend:YOUR_TAG
```

確認 workflow 已將映像部署至 Cloud Run。

## 疑難排解

### Cloud Run 啟動但資料庫存取回傳 500

- 確認 `DATABASE_URL` 已存入 Secret Manager 並注入至 Cloud Run。
- 確認 Cloud SQL 執行個體已掛載至 Cloud Run 服務。
- 確認執行個體連線名稱與實際 Cloud SQL 執行個體相符。
- 確認資料庫使用者與資料庫名稱存在。

### Cloud Run 無法啟動

- 確認 `ENVIRONMENT=production` 僅在正式環境下設定。
- 確認 `SECRET_KEY`、`JWT_SECRET_KEY`、`JWT_ACCESS_SECRET_KEY`、`JWT_REFRESH_SECRET_KEY` 均已設定。
- 確認服務容器監聽於 port `8080`。
- 查看 Cloud Run 日誌，確認 settings 或資料庫設定是否有載入時期錯誤。

### Cloud Build 成功但 Cloud Run 未更新

- `cloudbuild.yaml` 設計上僅負責建置。
- 建置輸出只會進入 Artifact Registry。
- 使用 Cloud Run 部署腳本、GitHub Actions 發布 job 或獨立的部署 trigger 來發布映像。

### Secret Manager 的值未出現在 Cloud Run

- 確認機密名稱完全一致。
- 確認 Cloud Run 服務帳號具有 `Secret Manager Secret Accessor` 權限。
- 更新機密值時需新增一個新版本。

### 瀏覽器出現 CORS 錯誤

- 確認 `CORS_ORIGINS` 包含正確的前端 origin，包含協定與 port。
- 多個 origin 以逗號分隔。
- 確認正式環境的前端 URL 未仍指向 localhost。

### 就緒檢查回傳 `degraded`

- 確認 Cloud SQL 執行個體可連線。
- 確認資料庫存在且憑證正確。
- 確認 Cloud Run 服務具有連線至資料庫的權限與網路存取能力。

## 注意事項

- `CORS_ORIGINS` 請與前端網域保持同步。
- 所有正式環境機密請存放於 Secret Manager。
- 發布前請先執行 migration，再開放真實流量。
- `service.yaml` 是保留作為參考用的舊版 manifest，不屬於目前 Cloud Run 部署流程的一部分。
