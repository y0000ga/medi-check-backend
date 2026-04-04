from typing import Generic, TypeVar
from pydantic import BaseModel

from app.core.enums.base import SortOrder

T = TypeVar("T")


class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    type: str

class ApiError(BaseModel):
    statusCode: int
    message: str
    # 來自 Fast API 的錯誤訊息
    details: list[ValidationErrorDetail] | None = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    error: ApiError | None
    data: T | None

class PaginationRequest(BaseModel):
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC

class PaginationResponse(BaseModel):
    page: int
    total_size: int
