from typing import Any

from app.core.enums.base import SortOrder


def apply_sort_order(stmt: Any, order_column: Any, sort_order: SortOrder):
    if sort_order == SortOrder.ASC:
        return stmt.order_by(order_column.asc())

    return stmt.order_by(order_column.desc())


def apply_pagination(stmt: Any, page: int, page_size: int) -> Any:
    offset = (page - 1) * page_size
    return stmt.offset(offset).limit(page_size)
