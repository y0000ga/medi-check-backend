from datetime import UTC, datetime
import uuid

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.session import get_db
from app.models.user_session import UserSession
from app.repositories.user_session import get_user_session_by_token_id
from app.services.errors.auth import (
    expired_refresh_token_error,
    invalid_refresh_token_error,
    revoked_refresh_token_error,
)


def validate_user_session(
    user_session: UserSession | None, user_id: uuid.UUID, refresh_token: str
) -> UserSession:
    # 如果找不到 -> refresh 失敗
    if not user_session:
        raise invalid_refresh_token_error()

    # 如果 revoked_at 不為空 -> refresh 失敗
    if user_session.revoked_at:
        raise revoked_refresh_token_error()

    # 如果 expires_at <= now -> refresh 失敗
    now = datetime.now(UTC)
    if user_session.expires_at <= now:
        raise expired_refresh_token_error()

    if user_session.user_id != user_id:
        raise invalid_refresh_token_error()

    # 驗證 raw refresh token 是否真的匹配 DB hash
    if not verify_password(refresh_token, user_session.refresh_token_hash):
        raise invalid_refresh_token_error()

    return user_session


def get_current_user_session(
    token_id: uuid.UUID,
    user_id: uuid.UUID,
    refresh_token: str,
    db: Session = Depends(get_db),
) -> UserSession:
    user_session = get_user_session_by_token_id(db=db, token_id=token_id)

    return validate_user_session(
        user_session=user_session, user_id=user_id, refresh_token=refresh_token
    )
