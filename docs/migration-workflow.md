# Migration 工作流程

本專案使用 Alembic 管理本機開發與正式環境的資料庫 schema 異動。

## 目標

- 讓 schema 在各環境間可重現
- 避免手動修改資料庫
- 讓每次 schema 異動都可在版本控制中審查
- 保持 Cloud Run 部署與 schema 異動的同步

## Migration 運作方式

- 應用程式從 settings 讀取 `DATABASE_URL`。
- Alembic 在 `migrations/env.py` 中使用相同的 `DATABASE_URL`。
- 本機開發通常指向 Docker 容器中的 PostgreSQL。
- 正式環境指向 Cloud SQL PostgreSQL 執行個體。

## 初次設定

當專案需要全新的 migration 歷史時：

1. 確認所有 SQLAlchemy model 都已在 `migrations/env.py` 中匯入
2. 確認 `Base.metadata` 包含所有需要 Alembic 追蹤的資料表
3. 產生第一個 revision：

```powershell
uv run alembic revision --autogenerate -m "initial schema"
```

4. 仔細審查產生的 migration 內容
5. 套用至目標資料庫：

```powershell
uv run alembic upgrade head
```

初次 migration 應從零開始建立完整的 schema。

## 標準異動流程

之後每次 schema 異動，請遵循以下流程：

1. 先修改 SQLAlchemy model
2. 若新 schema 影響行為，同步更新 repository 或 service 程式碼
3. 產生新的 revision：

```powershell
uv run alembic revision --autogenerate -m "describe the change"
```

4. 檢查產生的 migration 檔案
5. 若 Alembic 有遺漏或產生不安全的內容，手動修正 migration
6. 在本機執行 migration：

```powershell
uv run alembic upgrade head
```

7. 測試受影響的 API 流程
8. 將 model 異動與 migration 一起 commit

## 部署至 Cloud Run 前

當 schema 異動包含在某次發布中時：

1. 建置並推送新的映像
2. 對 Cloud SQL 資料庫執行 Alembic
3. 確認 migration 成功
4. 發布新的 Cloud Run revision

請勿依賴 Cloud Run 啟動時自動套用 migration。

## 正式環境 Migration 順序

安全的正式環境 migration 順序如下：

```powershell
uv run alembic current
uv run alembic upgrade head
```

若 schema 異動有風險，請在套用 migration 前備份資料庫。

## 每次 Migration 需審查的項目

- 資料表與欄位名稱
- 可為 null 與不可為 null 的異動
- 預設值
- 外鍵
- 唯一限制
- 索引
- Enum 異動
- 資料 migration 的安全性

## 注意事項

- 若異動應透過 Alembic 管理，請勿手動修改資料庫
- 請勿跳過審查 autogenerate 的輸出
- 將 model 異動與 migration 檔案放在同一個 pull request
- 若 migration 需要資料回填，請盡量讓操作明確且可還原
- Migration 需與 Cloud Run 所使用的 Cloud SQL 執行個體相容

## 本機開發

在本機開發時：

1. 啟動 PostgreSQL
2. 啟動應用程式前先套用 migration
3. 若 schema 有異動，重新產生並套用新的 revision
4. Migration 完成後，若有使用 pgAdmin 查看資料庫，請重新整理頁面

建議指令：

```powershell
docker compose up -d postgres
uv run alembic upgrade head
uv run fastapi dev
```

若 pgAdmin 中看不到資料表，請確認連線目標與 `.env` 中的資料庫一致：

- 主機：`localhost`
- Port：`5432`
- 資料庫：`medi_check`
- 使用者名稱：`medi_check_user`
- 密碼：依 `.env` 中的 `DATABASE_URL` 設定為準

接著展開 `Databases > medi_check > Schemas > public > Tables` 並重新整理樹狀結構。

## Cloud SQL 部署注意事項

- 使用 Cloud SQL PostgreSQL 執行個體作為正式環境的 migration 目標。
- 將 `DATABASE_URL` 存放於 Secret Manager 或其他安全的機密儲存服務。
- 若 schema 有異動，請在將新的 Cloud Run revision 對外開放前先執行 migration。

## 疑難排解

- 若 Alembic 顯示沒有目前 revision，資料庫可能是空的，或 version table 尚未存在
- 若 `autogenerate` 產生非預期的 diff，請確認所有 model 都已在 `migrations/env.py` 中匯入
- 若 migration 失敗，請先修正 migration 檔案，而非手動修改資料庫
- 若 pgAdmin 未顯示新建立的資料表，確認 migration 已成功完成並重新整理瀏覽器樹狀結構
- 若 Cloud Run 啟動但應用程式無法讀取資料，確認 Cloud SQL 執行個體與 `DATABASE_URL` 指向同一個資料庫

### 本機 PostgreSQL 密碼問題

**更改密碼後仍無法連線（`password authentication failed`）**

PostgreSQL 的帳號密碼在 volume 首次初始化時寫入，之後修改 `docker-compose.yml` 的 `POSTGRES_PASSWORD` 不會自動更新已存在的 volume。需刪除舊 volume 並重新建立：

```powershell
docker compose down -v
docker compose up -d
uv run alembic upgrade head
```

**密碼含特殊字元（`#`、`|`、`)` 等）導致連線失敗**

特殊字元在 YAML 和資料庫 URL 中可能造成解析問題。本機開發建議使用不含特殊字元的密碼，並確保 `docker-compose.yml` 與 `.env` 中的密碼完全一致。

目前本機開發密碼為 `medi_check_password`，pgAdmin 連線設定如下：

| 欄位 | 值 |
|------|-----|
| Host name/address | `localhost` |
| Port | `5432` |
| Maintenance database | `medi_check` |
| Username | `medi_check_user` |
| Password | `medi_check_password` |
