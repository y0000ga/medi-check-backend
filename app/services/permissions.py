from app.core.enums.care_relationship import PermissionLevel
from app.services.errors.permission import (
    admin_permission_denied_error,
    read_permission_denied_error,
    write_permission_denied_error,
)

_PERMISSION_LEVEL_RANK = {
    PermissionLevel.READ: 1,
    PermissionLevel.WRITE: 2,
    PermissionLevel.ADMIN: 3,
}


def ensure_permission_level_at_least(
    *,
    current_level: PermissionLevel,
    required_level: PermissionLevel,
) -> None:
    current_rank = _PERMISSION_LEVEL_RANK[current_level]
    required_rank = _PERMISSION_LEVEL_RANK[required_level]

    if current_rank >= required_rank:
        return

    if required_level == PermissionLevel.READ:
        raise read_permission_denied_error()

    if required_level == PermissionLevel.WRITE:
        raise write_permission_denied_error()

    raise admin_permission_denied_error()


def ensure_can_read(*, permission_level: PermissionLevel) -> None:
    ensure_permission_level_at_least(
        current_level=permission_level,
        required_level=PermissionLevel.READ,
    )


def ensure_can_write(*, permission_level: PermissionLevel) -> None:
    ensure_permission_level_at_least(
        current_level=permission_level,
        required_level=PermissionLevel.WRITE,
    )


def ensure_can_admin(*, permission_level: PermissionLevel) -> None:
    ensure_permission_level_at_least(
        current_level=permission_level,
        required_level=PermissionLevel.ADMIN,
    )
