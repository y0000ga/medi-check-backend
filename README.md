# Medi Check Backend

Medi Check Backend 是一個用 FastAPI 建立的後端專案，主要提供醫療照護相關的 API 與資料處理能力。

- 使用者登入與 refresh token session
- 病患資料管理
- 照護者資料管理
- 排程與記錄查詢
- 快速檢查與驗證
- 與照護關係相關的流程

## 技術棧

- Python 3.12 or 3.13
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- `uv`

## Windows 啟動注意事項

如果你在 Windows 上看到這種錯誤：

```text
ImportError: DLL load failed while importing _ssl
```

通常不是 `uvicorn` 壞掉，而是目前使用的 Python runtime 被系統政策封鎖了。這個專案只支援 Python 3.12 或 3.13，請先確認你的本機環境是這兩個版本之一。

建議流程如下：

1. 確認目前 Python 版本
   ```powershell
   python --version
   ```
2. 如果 `.venv` 是用錯的 Python 建出來的，先刪掉再重建
   ```powershell
   Remove-Item -Recurse -Force .venv
   uv sync
   ```
3. 如果你要把開發工具一起裝上，執行
   ```powershell
   uv sync --group dev
   ```
4. 啟動服務
   ```powershell
   uv run uvicorn app.main:app --reload
   ```

如果你的電腦同時安裝了多個 Python，請優先使用沒有被政策封鎖的 3.12 或 3.13。

## 專案啟動

### 1. 安裝依賴

```bash
uv sync
```

如果需要 Ruff、pytest、pyright 等開發工具：

```bash
uv sync --group dev
```

### 2. 準備資料庫

如果目前使用 SQLite，請確認 `app/db/session.py` 裡的設定：

```python
DATABASE_URL = "sqlite:///./app.db"
```

再執行 migration：

```bash
uv run alembic upgrade head
```

### 3. 啟動開發伺服器

```bash
uv run uvicorn app.main:app --reload
```

啟動後可以打開：

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### 4. 常用開發指令

Lint：

```bash
uv run ruff check .
```

測試：

```bash
uv run pytest
```

產生 OpenAPI YAML：

```bash
uv run python scripts/generate_swagger.py
```

## 文件導覽

- [docs/architecture.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/architecture.md)
- [docs/database-design.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/database-design.md)
- [docs/api-flow.md](https://github.com/y0000ga/medi-check-backend/blob/main/docs/api-flow.md)

## API 文件

- Swagger UI: `/docs`
- ReDoc: `/redoc`
