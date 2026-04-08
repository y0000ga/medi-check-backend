from app.core.exceptions import AppException


def medication_access_denied_error() -> AppException:
    return AppException(
        status_code=401,
        message="Cannot access Medication",
    )
