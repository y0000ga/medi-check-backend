from app.schemas.base import ValidationErrorDetail
from app.core.exceptions import AppException


def expired_access_token_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="access_token",
                message="access token has expired",
                type="token_expired",
            )
        ],
    )


def invalid_access_token_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="access_token",
                message="Invalid Access Token",
                type="invalid_token",
            )
        ],
    )
