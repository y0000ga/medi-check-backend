FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

# 先複製 dependency 定義，以利用 Docker layer cache。
COPY pyproject.toml uv.lock ./

# 只安裝 dependency，不在此階段安裝專案本身。
RUN uv sync --frozen --no-install-project

# 複製 application、Alembic migration 等專案檔案。
COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]