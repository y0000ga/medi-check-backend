# Medi Check Backend — Agent Context

這份文件提供給 code agent 開發參考用。

---

## 1. 專案概覽

**產品名稱：** Medi Check
**類型：** 藥品提醒與服藥管理 API 後端
**框架：** FastAPI（Python）
**ORM：** SQLAlchemy + Alembic（PostgreSQL）
**Auth：** JWT Access Token + Refresh Token Rotation
**Schema 驗證：** Pydantic

---

## 2. 目錄結構

\`\`\`
app/
  api/routes/         # HTTP 路由
  core/               # 安全、例外處理、共用工具
  db/                 # SQLAlchemy Base / Session
  dependencies/       # FastAPI dependency injection
  models/             # 資料表模型
  repositories/       # DB 查詢
  schemas/            # Pydantic schema
  services/           # 商業邏輯
migrations/           # Alembic migration
docs/
  openapi.json        # API schema（自動產生）
\`\`\`

---

## 3. 分層架構

| 層級 | 路徑 | 職責 |
|------|------|------|
| Routes | `app/api/routes/` | 接收 HTTP request，回傳 response |
| Services | `app/services/` | 商業邏輯、權限驗證、交易流程 |
| Repositories | `app/repositories/` | DB 查詢與寫入，不含商業邏輯 |
| Models | `app/models/` | 資料表模型 |
| Schemas | `app/schemas/` | Pydantic request/response schema |
| Core | `app/core/` | 共用工具、例外處理、安全邏輯 |

---

## 4. 資料流

1. Route 層接收請求，解析 path / query / body
2. Route 層組裝 payload schema
3. Service 層進行權限驗證與商業邏輯處理
4. Repository 層執行查詢或寫入
5. Service 層組裝 response DTO
6. Route 層透過 `success_response(...)` 包成統一格式回傳

---

## 5. 重要設計決策

### 權限驗證集中在 Service 層
不要在 Route 層做權限判斷，統一使用：
- `validate_patient_access(...)`
- `validate_medication_access(...)`
- `ensure_can_read(...)`
- `ensure_can_write(...)`

### Schedule 與 History 分離
- `schedules`：規則層，不預先展開 event
- `histories`：結果層，只有實際發生的事件才建立
- `GET /schedule-matches`：後端動態展開 event instance 並合併 history
- 前端不自己計算排程規則

### History 快照設計
建立 history 時保留以下快照欄位：
- `amount_snapshot`
- `dose_unit_snapshot`
- `medication_name_snapshot`
- `medication_dosage_form_snapshot`
- `source`：quickCheck / manual / system

### Token 傳遞
- 不依賴 cookie
- 透過 response / request body 傳遞
- Mobile client 存放於安全儲存區

---

## 6. Migration 管理

```bash
# 套用所有 migration
uv run alembic upgrade head

# 自動產生新的 migration
uv run alembic revision --autogenerate -m "describe change"
```

---

## 7. 開發注意事項

1. API 有變動後，更新 `docs/openapi.json`：
   `curl http://localhost:8000/openapi.json > docs/openapi.json`
2. 資料庫 schema 變動必須建立 Alembic migration
3. 所有 response 使用統一格式 `success_response(...)`
4. 新增 API 端點後，同步更新 `shared-docs/Medi_Check_技術規格書.md`

---

## 8. 文件路徑

此檔案（AGENT_CONTEXT.md）位於後端專案根目錄。

共用文件放在 `shared-docs/` 目錄下：

| 文件 | 路徑 |
|------|------|
| 產品規格書 | `shared-docs/Medi_Check_產品規格書.md` |
| 技術規格書 | `shared-docs/Medi_Check_技術規格書.md` |
| 設計系統 | `shared-docs/DESIGN.md` |

### API Schema
openapi.json 位於本專案的 `docs/openapi.json`，
同時也發佈於：
https://raw.githubusercontent.com/y0000ga/medi-check-backend/main/docs/openapi.json