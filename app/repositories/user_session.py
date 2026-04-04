import uuid

from datetime import UTC, datetime
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.models.user_session import UserSession


def create_user_session(
    db: Session,
    user_id: uuid.UUID,
    refresh_token_hash: str,
    user_agent: str | None,
    ip_address: str | None,
    expires_at: datetime,
    tid: uuid.UUID,
) -> UserSession:
    user_session = UserSession(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at,
        token_id=tid,
    )
    db.add(user_session)
    db.flush()
    return user_session


def delete_inactive_sessions_by_user_id(db: Session, user_id: uuid.UUID) -> None:
    now = datetime.now(UTC)
    db.execute(
        delete(UserSession).where(
            UserSession.user_id == user_id,
            or_(UserSession.revoked_at.is_not(None), UserSession.expires_at <= now),
        ),
    )


def get_user_session_by_token_id(db: Session, token_id: uuid.UUID) -> UserSession | None:
    result = db.execute(
        select(UserSession).where(UserSession.token_id == token_id)
    )
    return result.scalar_one_or_none()
