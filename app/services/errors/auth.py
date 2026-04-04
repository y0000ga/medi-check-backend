from app.schemas.base import ValidationErrorDetail
from app.core.exceptions import AppException

def duplicate_email_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="email",
                message="Email already exists",
                type="duplicate",
            )
        ],
    )


def sign_up_failed_error() -> AppException:
    return AppException(
        status_code=500,
        message="Failed to sign up",
    )


def invalid_credentials_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="non_field_error",
                message="Invalid email or password",
                type="invalid_credentials",
            )
        ],
    )

def invalid_user_status() -> AppException:
    return AppException(
        status_code=401,
        message="Disabled User",
    )

def sign_in_failed_error() -> AppException:
    return AppException(
        status_code=500,
        message="Failed to sign in",
    )


def invalid_refresh_token_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="refresh_token",
                message="Invalid refresh token",
                type="invalid_token",
            )
        ],
    )


def expired_refresh_token_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="refresh_token",
                message="Refresh token has expired",
                type="token_expired",
            )
        ],
    )


def revoked_refresh_token_error() -> AppException:
    return AppException(
        status_code=401,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="refresh_token",
                message="Refresh token has been revoked",
                type="revoked_token",
            )
        ],
    )


def refresh_failed_error() -> AppException:
    return AppException(
        status_code=500,
        message="Failed to refresh token",
    )

