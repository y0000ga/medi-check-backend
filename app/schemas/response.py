from app.schemas.base import ApiResponse

def success_response(data):
    return ApiResponse(
        success=True,
        error=None,
        data=data,
    )
