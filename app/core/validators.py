from app.core.exceptions import AppException
from app.schemas.base import ValidationErrorDetail


def _field_validation_error(field_name: str, message: str, error_type: str) -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field=field_name,
                message=message,
                type=error_type,
            )
        ],
    )


def validate_required_string_field(
    value: str | None,
    field_name: str,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    trim: bool = True,
) -> str:
    if value is None:
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} is required",
            error_type="required",
        )

    normalized_value = value.strip() if trim else value

    if normalized_value == "":
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} cannot be empty",
            error_type="empty",
        )

    if min_length is not None and len(normalized_value) < min_length:
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} must be at least {min_length} characters long",
            error_type="too_short",
        )
    if max_length is not None and len(normalized_value) > max_length:
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} must be at most {max_length} characters long",
            error_type="too_long",
        )
    return normalized_value


def validate_optional_string_field(
    value: str | None,
    field_name: str,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    trim: bool = True,
    empty_as_none: bool = False,
) -> str | None:
    if value is None:
        return None

    normalized_value = value.strip() if trim else value

    if normalized_value == "":
        if empty_as_none:
            return None
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} cannot be empty",
            error_type="empty",
        )

    if min_length is not None and len(normalized_value) < min_length:
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} must be at least {min_length} characters long",
            error_type="too_short",
        )
    if max_length is not None and len(normalized_value) > max_length:
        raise _field_validation_error(
            field_name=field_name,
            message=f"{field_name} must be at most {max_length} characters long",
            error_type="too_long",
        )
    return normalized_value
