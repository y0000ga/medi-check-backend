from app.core.exceptions import AppException


def permission_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Permission denied",
    )
