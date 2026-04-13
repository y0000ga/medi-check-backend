from app.core.exceptions import AppException


def patient_not_found_error() -> AppException:
    return AppException(
        status_code=404,
        message="Patient not found",
    )


def patient_access_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Cannot access Patient",
    )


def current_user_patient_not_found_error() -> AppException:
    return AppException(
        status_code=404,
        message="Patient not found for current user",
    )
