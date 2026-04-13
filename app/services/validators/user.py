# 驗證合理存在的 user
from app.core.enums.user import UserStatus
from app.models import User
from app.services.errors.auth import disabled_user_error, invited_user_error
from app.services.errors.user import invalid_access_token_error


def validate_active_user(user: User | None) -> User:
    # 使用者不存在
    if not user:
        raise invalid_access_token_error()
    # 使用者 DISABLED
    if user.status == UserStatus.INVITED:
        raise invited_user_error()

    if user.status == UserStatus.DISABLED:
        raise disabled_user_error()

    return user
