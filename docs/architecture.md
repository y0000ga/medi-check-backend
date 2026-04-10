# 專案架構

## 分層設計

- `app/api/routes`：接收 HTTP request，轉成 payload，回傳 API response
- `app/services`：處理商業邏輯、權限驗證、交易流程與 response 組裝
- `app/repositories`：處理 SQLAlchemy 查詢與資料存取
- `app/models`：定義資料表模型
- `app/schemas`：定義 request / response schema
- `app/dependencies`：FastAPI 的 dependency injection
- `app/core`：共用工具、例外處理、安全邏輯與 validator

## 專案結構

```text
app/
  api/routes/         # HTTP 路由
  core/               # 安全、例外處理、共用工具
  db/                 # SQLAlchemy Base / Session
  dependencies/       # FastAPI dependency
  models/             # 資料表模型
  repositories/       # DB query
  schemas/            # Pydantic schema
  services/           # 商業邏輯
migrations/           # Alembic migration
scripts/              # 輔助腳本
```

## 後端內部資料流

大多數 API 會遵守這個流程：

1. Route layer 接 request，解析 path、query、body。
2. Route layer 建立 payload schema。
3. Service layer 驗證權限與商業規則。
4. Repository layer 執行查詢或寫入。
5. Service layer 組裝 response schema。
6. Route layer 用 `success_response(...)` 包成統一格式。

這樣做的目的有幾個：

- 避免 route 直接塞滿商業邏輯
- 讓權限驗證集中在 service / validator
- 讓查詢邏輯可以被重用
- 讓 schema 與 DB model 不直接耦合

## 目前的核心設計概念

### 1. 權限不是寫在 route 裡

route 主要只處理 request mapping。真正的權限判斷通常在：

- `validate_patient_access(...)`
- `validate_medication_access(...)`
- `ensure_can_read(...)`
- `ensure_can_write(...)`

這讓權限邏輯比較不會分散。

### 2. `schedule` 和 `history` 是不同層級的資料

這是專案很重要的設計點：

- `schedule`：定義規則
- `history`：定義某次具體事件的結果

也就是說：

- schedule 回答「應該什麼時候吃」
- history 回答「那次到底有沒有吃」

### 3. Frontend 盡量不要自己實作排程規則

目前 `GET /schedule-matches` 的方向，是讓 backend 直接回傳展開後的 event instance，再附上對應 history。

這樣前端就不需要自己處理：

- recurrence 規則驗證
- 合法事件判斷
- history merge

### 4. 歷史紀錄採 snapshot 設計

`histories` 不是只存 foreign key，也會把當下的重要資訊一起存進來，例如：

- `amount_snapshot`
- `dose_unit_snapshot`
- `medication_name_snapshot`
- `medication_dosage_form_snapshot`

這樣就算後來藥名或排程規則改了，歷史紀錄仍然保留當時的真實內容。
