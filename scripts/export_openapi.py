from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Avoid using production settings while generating docs in CI/local.
os.environ.setdefault("ENVIRONMENT", "documentation")
os.environ.setdefault("DATABASE_URL", "sqlite:///./docs-generation.db")
os.environ.setdefault("SECRET_KEY", "docs-generation-secret")
os.environ.setdefault("JWT_SECRET_KEY", "docs-generation-secret")
os.environ.setdefault("JWT_ACCESS_SECRET_KEY", "docs-generation-secret")
os.environ.setdefault("JWT_REFRESH_SECRET_KEY", "docs-generation-secret")
os.environ.setdefault("CORS_ORIGINS", "*")

from app.main import app


DOCS_DIR = PROJECT_ROOT / "docs"
OPENAPI_JSON_PATH = DOCS_DIR / "openapi.json"
OPENAPI_YAML_PATH = DOCS_DIR / "openapi.yaml"


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    schema = app.openapi()

    OPENAPI_JSON_PATH.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    OPENAPI_YAML_PATH.write_text(
        yaml.safe_dump(
            schema,
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    print(f"Generated {OPENAPI_JSON_PATH}")
    print(f"Generated {OPENAPI_YAML_PATH}")


if __name__ == "__main__":
    main()