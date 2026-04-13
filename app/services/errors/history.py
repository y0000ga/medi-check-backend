from app.core.exceptions import AppException
from app.schemas.base import ValidationErrorDetail


def invalid_quick_check_schedule_event_error() -> AppException:
    return _history_validation_error(
        field="scheduled_at",
        message="scheduled_at does not match the schedule",
        type="invalid",
    )


def duplicate_quick_check_history_error() -> AppException:
    return AppException(
        status_code=409,
        message="History already exists for this schedule event",
        details=[
            ValidationErrorDetail(
                field="scheduled_at",
                message="history already exists for this schedule event",
                type="duplicate",
            )
        ],
    )


def history_not_found_error() -> AppException:
    return AppException(
        status_code=404,
        message="History not found",
    )


def history_access_denied_error() -> AppException:
    return AppException(
        status_code=403,
        message="Cannot access History",
    )


def invalid_quick_check_feeling_error() -> AppException:
    return _history_validation_error(
        field="feeling",
        message="feeling must be between 1 and 5",
        type="invalid",
    )


def invalid_quick_check_taken_amount_error() -> AppException:
    return _history_validation_error(
        field="taken_amount",
        message="taken_amount must be greater than 0",
        type="invalid",
    )


def invalid_history_feeling_error() -> AppException:
    return _history_validation_error(
        field="feeling",
        message="feeling must be between 1 and 5",
        type="invalid",
    )


def invalid_history_taken_amount_error() -> AppException:
    return _history_validation_error(
        field="taken_amount",
        message="taken_amount must be greater than 0",
        type="invalid",
    )


def _history_validation_error(
    *,
    field: str,
    message: str,
    type: str,
) -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field=field,
                message=message,
                type=type,
            )
        ],
    )
