def validate_required_string_field(
    value: str | None,
    field_name: str,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    trim: bool = True,
) -> str:
    if value is None:
        raise ValueError(f"{field_name} is required")

    normalized_value = value.strip() if trim else value

    if normalized_value == "":
        raise ValueError(f"{field_name} cannot be empty")

    if normalized_value == "":
        return normalized_value

    if min_length is not None and len(normalized_value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    if max_length is not None and len(normalized_value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long")
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
        raise ValueError(f"{field_name} cannot be empty")

    if min_length is not None and len(normalized_value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    if max_length is not None and len(normalized_value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long")
    return normalized_value
