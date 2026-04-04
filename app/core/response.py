from typing import TypeVar

from app.schemas.base import ApiError, ApiResponse, ValidationErrorDetail

T = TypeVar("T")


def success_response(data: T) -> ApiResponse[T]:
    return ApiResponse(
        success=True,
        error=None,
        data=data,
    )


def error_response(
    status_code: int,
    message: str,
    details: list[ValidationErrorDetail] | None = None,
) -> ApiResponse[None]:
    return ApiResponse(
        success=False,
        error=ApiError(
            statusCode=status_code,
            message=message,
            details=details,
        ),
        data=None,
    )
