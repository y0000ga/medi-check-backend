from typing import Any

from app.schemas.base import ApiResponse

def success_response(data: Any) -> ApiResponse[Any]:
    return ApiResponse(
        success=True,
        error=None,
        data=data,
    )
