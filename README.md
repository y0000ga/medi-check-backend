# Medi Check Backend

Medi Check Backend 是一個以 FastAPI 為核心的後端服務，負責處理用藥追蹤相關功能，包含：

- 使用者註冊、登入、登出與 refresh token session
- 病患管理
- 藥物管理
- 用藥排程管理
- 服藥紀錄與 quick check
- 照護邀請與照護關係

## 技術棧

- Python 3.14+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- `uv`

## 專案啟動

### 1. 安裝依賴

```bash
uv sync
```

如果你也需要 Ruff、Pytest、Pyright：

```bash
uv sync --group dev
```

### 2. 準備資料庫

目前專案預設使用 SQLite，設定位置在 app/db/session.py。

```python
DATABASE_URL = "sqlite:///./app.db"
```

執行 migration：

```bash
uv run alembic upgrade head
```

### 3. 啟動開發伺服器

```bash
uv run uvicorn app.main:app --reload
```

啟動後可使用：

- API：`http://localhost:8000`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- Health Check：`http://localhost:8000/health`

### 4. 常用開發指令

Lint：

```bash
uv run ruff check .
```

測試：

```bash
uv run pytest
```

重新產生 OpenAPI YAML：

```bash
uv run python scripts/generate_swagger.py
```

## 文件導覽

如果你想快速理解專案，建議依序閱讀：

- [docs/architecture.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/architecture.md)：專案分層、模組責任與核心設計概念
- [docs/database-design.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/database-design.md)：資料表設計、關聯與 `schedule` / `history` 建模思路
- [docs/api-flow.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/api-flow.md)：主要 API 流程與前後端資料流

## API 文件

- Swagger UI：`/docs`
- ReDoc：`/redoc`