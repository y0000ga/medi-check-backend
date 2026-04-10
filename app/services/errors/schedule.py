from app.core.exceptions import AppException
from app.schemas.base import ValidationErrorDetail


def _schedule_validation_error(
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


def schedule_access_denied_error() -> AppException:
    return AppException(
        status_code=401,
        message="Cannot access Schedule",
    )


def invalid_schedule_event_date_range_error() -> AppException:
    return _schedule_validation_error(
        field="to_date",
        message="to_date must be greater than or equal to from_date",
        type="invalid",
    )


def schedule_event_date_range_too_large_error() -> AppException:
    return _schedule_validation_error(
        field="to_date",
        message="schedule event date range must not exceed 7 days",
        type="invalid",
    )


def start_date_required_error() -> AppException:
    return _schedule_validation_error(
        field="start_date",
        message="start_date is required",
        type="required",
    )


def time_slots_required_error() -> AppException:
    return _schedule_validation_error(
        field="time_slots",
        message="time_slots is required",
        type="required",
    )


def frequency_unit_not_allowed_for_one_time_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="frequency_unit",
        message="frequency_unit is not allowed for one-time schedules",
        type="not_allowed",
    )


def interval_not_allowed_for_one_time_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="interval",
        message="interval is not allowed for one-time schedules",
        type="not_allowed",
    )


def weekdays_not_allowed_for_one_time_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="weekdays",
        message="weekdays is not allowed for one-time schedules",
        type="not_allowed",
    )


def until_date_not_allowed_for_one_time_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="until_date",
        message="until_date is not allowed for one-time schedules",
        type="not_allowed",
    )


def occurrence_count_not_allowed_for_one_time_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="occurrence_count",
        message="occurrence_count is not allowed for one-time schedules",
        type="not_allowed",
    )


def frequency_unit_required_for_recurring_schedule_error() -> AppException:
    return _schedule_validation_error(
        field="frequency_unit",
        message="frequency_unit is required for recurring schedules",
        type="required",
    )


def invalid_recurring_interval_error() -> AppException:
    return _schedule_validation_error(
        field="interval",
        message="interval must be greater than 0 for recurring schedules",
        type="invalid",
    )


def weekdays_required_for_week_frequency_error() -> AppException:
    return _schedule_validation_error(
        field="weekdays",
        message="weekdays is required when frequency_unit is week",
        type="required",
    )


def duplicate_weekdays_error() -> AppException:
    return _schedule_validation_error(
        field="weekdays",
        message="weekdays must not contain duplicate values",
        type="duplicate",
    )


def invalid_weekdays_range_error() -> AppException:
    return _schedule_validation_error(
        field="weekdays",
        message="weekdays must contain values from 1 to 7",
        type="invalid",
    )


def weekdays_only_allowed_for_week_frequency_error() -> AppException:
    return _schedule_validation_error(
        field="weekdays",
        message="weekdays is only allowed when frequency_unit is week",
        type="not_allowed",
    )


def until_date_not_allowed_for_never_end_error() -> AppException:
    return _schedule_validation_error(
        field="until_date",
        message="until_date is not allowed when end_type is never",
        type="not_allowed",
    )


def occurrence_count_not_allowed_for_never_end_error() -> AppException:
    return _schedule_validation_error(
        field="occurrence_count",
        message="occurrence_count is not allowed when end_type is never",
        type="not_allowed",
    )


def occurrence_count_required_for_counts_end_error() -> AppException:
    return _schedule_validation_error(
        field="occurrence_count",
        message="occurrence_count is required when end_type is counts",
        type="required",
    )


def invalid_occurrence_count_error() -> AppException:
    return _schedule_validation_error(
        field="occurrence_count",
        message="occurrence_count must be greater than 1",
        type="invalid",
    )


def until_date_not_allowed_for_counts_end_error() -> AppException:
    return _schedule_validation_error(
        field="until_date",
        message="until_date is not allowed when end_type is counts",
        type="not_allowed",
    )


def occurrence_count_not_allowed_for_until_end_error() -> AppException:
    return _schedule_validation_error(
        field="occurrence_count",
        message="occurrence_count is not allowed when end_type is until",
        type="not_allowed",
    )


def until_date_required_for_until_end_error() -> AppException:
    return _schedule_validation_error(
        field="until_date",
        message="until_date is required when end_type is until",
        type="required",
    )


def until_date_before_start_date_error() -> AppException:
    return _schedule_validation_error(
        field="until_date",
        message="until_date must be later than start_date",
        type="invalid",
    )
