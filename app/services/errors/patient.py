from app.core.exceptions import AppException
from app.schemas.base import ValidationErrorDetail


def patient_access_denied_error() -> AppException:
    return AppException(
        status_code=401,
        message="Cannot access Patient",
    )


def current_user_patient_not_found_error() -> AppException:
    return AppException(
        status_code=500,
        message="Patient not found for current user",
    )


def patient_email_requires_invitation_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="email",
                message=(
                    "This email already has an account. Please use the invitation "
                    "flow instead"
                ),
                type="invalid",
            )
        ],
    )
