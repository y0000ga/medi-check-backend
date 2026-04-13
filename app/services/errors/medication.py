from app.core.exceptions import AppException


def medication_not_found_error() -> AppException:
    return AppException(
        status_code=404,
        message="Medication not found",
    )


def medication_access_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Cannot access Medication",
    )
