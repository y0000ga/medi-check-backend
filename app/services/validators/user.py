# 驗證合理存在的 user
from app.core.enums.user import UserStatus
from app.models import User
from app.services.errors.auth import invalid_user_status
from app.services.errors.user import invalid_access_token_error


def validate_active_user(user: User | None) -> User:
    # 使用者不存在
    if not user:
        raise invalid_access_token_error()
    # 使用者 DISABLED
    if user.status == UserStatus.DISABLED:
        raise invalid_user_status()

    return user