from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app


def _quote_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_key(value: Any) -> str:
    return _quote_string(str(value))


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return _quote_string(str(value))


def _to_yaml(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent

    if isinstance(value, dict):
        if not value:
            return [prefix + "{}"]

        lines: list[str] = []
        for key, item in value.items():
            key_text = _format_key(key)
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key_text}:")
                lines.extend(_to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}{key_text}: {_format_scalar(item)}")
        return lines

    if isinstance(value, list):
        if not value:
            return [prefix + "[]"]

        lines = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(prefix + "- {}")
                    continue

                first = True
                for key, nested in item.items():
                    key_text = _format_key(key)
                    if first:
                        if isinstance(nested, (dict, list)):
                            lines.append(f"{prefix}- {key_text}:")
                            lines.extend(_to_yaml(nested, indent + 4))
                        else:
                            lines.append(f"{prefix}- {key_text}: {_format_scalar(nested)}")
                        first = False
                    else:
                        if isinstance(nested, (dict, list)):
                            lines.append(f"{prefix}  {key_text}:")
                            lines.extend(_to_yaml(nested, indent + 4))
                        else:
                            lines.append(f"{prefix}  {key_text}: {_format_scalar(nested)}")
            elif isinstance(item, list):
                lines.append(prefix + "-")
                lines.extend(_to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_format_scalar(item)}")
        return lines

    return [prefix + _format_scalar(value)]


def main() -> None:
    schema = app.openapi()
    output = "\n".join(_to_yaml(schema)) + "\n"
    Path("swagger.yaml").write_text(output, encoding="utf-8")
    print("swagger.yaml generated")


if __name__ == "__main__":
    main()
