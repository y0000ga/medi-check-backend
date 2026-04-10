# schedule = Schedule(
#     patient_id=patient_id,
#     medication_id=medication_id,
#     timezone=timezone,
#     start_date=start_date,
#     time_slots=time_slots,
#     dose_unit=dose_unit,
#     frequency=frequency,
#     interval=interval,
#     weekdays=weekdays,
#     end_type=end_type,
#     until_date=until_date,
#     occurance_count=occurance_count,
# )


from datetime import date

from app.core.enums.schedule import EndType, FrequencyUnit
from app.core.exceptions import AppException
from app.services.errors.schedule import (
    duplicate_weekdays_error,
    frequency_unit_not_allowed_for_one_time_schedule_error,
    frequency_unit_required_for_recurring_schedule_error,
    interval_not_allowed_for_one_time_schedule_error,
    invalid_occurrence_count_error,
    invalid_recurring_interval_error,
    invalid_weekdays_range_error,
    occurrence_count_not_allowed_for_never_end_error,
    occurrence_count_not_allowed_for_one_time_schedule_error,
    occurrence_count_not_allowed_for_until_end_error,
    occurrence_count_required_for_counts_end_error,
    start_date_required_error,
    time_slots_required_error,
    until_date_before_start_date_error,
    until_date_not_allowed_for_counts_end_error,
    until_date_not_allowed_for_never_end_error,
    until_date_not_allowed_for_one_time_schedule_error,
    until_date_required_for_until_end_error,
    weekdays_not_allowed_for_one_time_schedule_error,
    weekdays_only_allowed_for_week_frequency_error,
    weekdays_required_for_week_frequency_error,
)


def _ensure_rules(rules: list[tuple[bool, AppException]]) -> None:
    for condition, error in rules:
        if not condition:
            raise error


def _validate_frequency_rule(
    *,
    frequency_unit: FrequencyUnit | None,
    weekdays: list[int] | None,
) -> None:
    if frequency_unit != FrequencyUnit.week:
        _ensure_rules(
            [(weekdays is None, weekdays_only_allowed_for_week_frequency_error())]
        )
        return

    _ensure_rules(
        [
            (
                weekdays is not None and len(weekdays) > 0,
                weekdays_required_for_week_frequency_error(),
            ),
            (
                weekdays is not None and len(set(weekdays)) == len(weekdays),
                duplicate_weekdays_error(),
            ),
            (
                weekdays is not None and all(1 <= weekday <= 7 for weekday in weekdays),
                invalid_weekdays_range_error(),
            ),
        ]
    )


def _validate_one_time_rules(
    *,
    time_slots: list[str] | None,
    frequency_unit: FrequencyUnit | None,
    interval: int | None,
    weekdays: list[int] | None,
    until_date: date | None,
    occurrence_count: int | None,
) -> None:
    _ensure_rules(
        [
            (time_slots is not None and len(time_slots) > 0, time_slots_required_error()),
            (
                until_date is None,
                until_date_not_allowed_for_one_time_schedule_error(),
            ),
            (
                occurrence_count is None,
                occurrence_count_not_allowed_for_one_time_schedule_error(),
            ),
            (
                frequency_unit is None,
                frequency_unit_not_allowed_for_one_time_schedule_error(),
            ),
            (interval is None, interval_not_allowed_for_one_time_schedule_error()),
            (
                weekdays is None or len(weekdays) == 0,
                weekdays_not_allowed_for_one_time_schedule_error(),
            ),
        ]
    )


def _validate_recurring_base_rules(
    *,
    time_slots: list[str] | None,
    frequency_unit: FrequencyUnit | None,
    interval: int | None,
    weekdays: list[int] | None,
) -> None:
    _ensure_rules(
        [
            (time_slots is not None and len(time_slots) > 0, time_slots_required_error()),
            (
                frequency_unit is not None,
                frequency_unit_required_for_recurring_schedule_error(),
            ),
            (
                interval is not None and interval > 0,
                invalid_recurring_interval_error(),
            ),
        ]
    )
    _validate_frequency_rule(frequency_unit=frequency_unit, weekdays=weekdays)


def _validate_never_end_rules(
    *,
    until_date: date | None,
    occurrence_count: int | None,
) -> None:
    _ensure_rules(
        [
            (until_date is None, until_date_not_allowed_for_never_end_error()),
            (
                occurrence_count is None,
                occurrence_count_not_allowed_for_never_end_error(),
            ),
        ]
    )


def _validate_counts_end_rules(
    *,
    until_date: date | None,
    occurrence_count: int | None,
) -> None:
    _ensure_rules(
        [
            (
                occurrence_count is not None,
                occurrence_count_required_for_counts_end_error(),
            ),
            (
                occurrence_count is not None and occurrence_count > 1,
                invalid_occurrence_count_error(),
            ),
            (until_date is None, until_date_not_allowed_for_counts_end_error()),
        ]
    )


def _validate_until_end_rules(
    *,
    until_date: date | None,
    start_date: date,
    occurrence_count: int | None,
) -> None:
    _ensure_rules(
        [
            (
                occurrence_count is None,
                occurrence_count_not_allowed_for_until_end_error(),
            ),
            (until_date is not None, until_date_required_for_until_end_error()),
            (
                until_date is not None and until_date > start_date,
                until_date_before_start_date_error(),
            ),
        ]
    )


def validate_create_schedule_rules(
    *,
    time_slots: list[str] | None,
    interval: int | None,
    frequency_unit: FrequencyUnit | None,
    weekdays: list[int] | None,
    end_type: EndType | None,
    until_date: date | None,
    start_date: date | None,
    occurrence_count: int | None,
) -> None:
    if start_date is None:
        raise start_date_required_error()

    if end_type is None:
        _validate_one_time_rules(
            time_slots=time_slots,
            frequency_unit=frequency_unit,
            interval=interval,
            weekdays=weekdays,
            until_date=until_date,
            occurrence_count=occurrence_count,
        )
        return

    _validate_recurring_base_rules(
        time_slots=time_slots,
        frequency_unit=frequency_unit,
        interval=interval,
        weekdays=weekdays,
    )

    if end_type == EndType.never:
        _validate_never_end_rules(
            until_date=until_date,
            occurrence_count=occurrence_count,
        )
        return

    if end_type == EndType.counts:
        _validate_counts_end_rules(
            until_date=until_date,
            occurrence_count=occurrence_count,
        )
        return

    if end_type == EndType.until:
        _validate_until_end_rules(
            until_date=until_date,
            start_date=start_date,
            occurrence_count=occurrence_count,
        )
