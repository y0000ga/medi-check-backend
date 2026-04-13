from app.core.exceptions import AppException


def read_permission_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Read permission denied",
    )


def write_permission_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Write permission denied",
    )


def admin_permission_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Admin permission denied",
    )
