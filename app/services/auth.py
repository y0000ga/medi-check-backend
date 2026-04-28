import logging
import uuid
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expires_at,
    hash_password,
    parse_refresh_token_ids,
    verify_password,
)
from app.core.validators import validate_required_string_field
from app.repositories.patient import create_patient_for_user
from app.repositories.user import create_user, get_user_by_email
from app.repositories.user_session import (
    create_user_session,
    delete_inactive_sessions_by_user_id,
    get_user_session_by_token_id,
)
from app.schemas.auth import (
    LogoutPayload,
    RefreshPayload,
    RefreshServiceResult,
    SignInPayload,
    SignInServiceResult,
    SignUpPayload,
    SignUpServiceResult,
)
from app.services.errors.auth import (
    duplicate_email_error,
    invalid_credentials_error,
    invalid_refresh_token_error,
    refresh_failed_error,
    sign_in_failed_error,
    sign_up_failed_error,
)
from app.services.validators.auth import get_valid_user_session
from app.services.validators.user import validate_active_user
from app.validation.rules import NAME_RULE, PASSWORD_RULE

logger = logging.getLogger(__name__)


def _is_duplicate_email_integrity_error(exc: IntegrityError) -> bool:
    error_message = str(getattr(exc, "orig", exc)).lower()
    if "users.email" in error_message:
        return True
    if "duplicate key value violates unique constraint" in error_message:
        return "email" in error_message
    if "unique constraint failed" in error_message:
        return "email" in error_message
    return False


def sign_up_user(
    payload: SignUpPayload, request: Request, db: Session
) -> SignUpServiceResult:
    try:
        normalized_email = payload.email.strip().lower()
        existing_user = get_user_by_email(db=db, email=normalized_email)
        if existing_user:
            logger.warning(
                "Duplicate signup email matched existing user",
                extra={
                    "email": normalized_email,
                    "existing_user_id": str(existing_user.id),
                    "existing_user_email": str(existing_user.email),
                    "existing_user_status": str(existing_user.status),
                },
            )
            raise duplicate_email_error()

        normalized_name = validate_required_string_field(
            value=payload.name,
            field_name="name",
            rule=NAME_RULE,
        )
        normalized_password = validate_required_string_field(
            value=payload.password,
            field_name="password",
            rule=PASSWORD_RULE,
        )
        normalized_birth_date = payload.birth_date
        hashed_password = hash_password(normalized_password)

        user = create_user(
            db=db,
            email=normalized_email,
            name=normalized_name,
            password_hash=hashed_password,
            birth_date=normalized_birth_date,
        )

        create_patient_for_user(
            db=db,
            user_id=user.id,
            name=user.name,
            birth_date=normalized_birth_date,
        )

        new_token_id = uuid.uuid4()
        new_refresh_token = create_refresh_token(
            user_id=user.id,
            token_id=new_token_id,
        )
        new_refresh_expires_at = get_refresh_token_expires_at()

        create_user_session(
            db=db,
            user_id=user.id,
            refresh_token_hash=hash_password(new_refresh_token),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
            expires_at=new_refresh_expires_at,
            tid=new_token_id,
        )

        db.commit()
    except AppException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        if _is_duplicate_email_integrity_error(exc):
            raise duplicate_email_error()
        raise
    except Exception:
        db.rollback()
        raise sign_up_failed_error()

    return SignUpServiceResult(
        user_id=user.id,
        refresh_token=new_refresh_token,
        access_token=create_access_token(user_id=user.id),
    )


def sign_in_user(
    payload: SignInPayload, request: Request, db: Session
) -> SignInServiceResult:
    try:
        normalized_email = payload.email.strip().lower()
        current_user = get_user_by_email(db=db, email=normalized_email)
        user = validate_active_user(user=current_user)

        is_valid_password = verify_password(payload.password, user.password_hash)
        if not is_valid_password:
            raise invalid_credentials_error()

        delete_inactive_sessions_by_user_id(user_id=user.id, db=db)
        new_token_id = uuid.uuid4()
        new_refresh_token = create_refresh_token(
            user_id=user.id,
            token_id=new_token_id,
        )
        new_refresh_expires_at = get_refresh_token_expires_at()
        create_user_session(
            db=db,
            user_id=user.id,
            refresh_token_hash=hash_password(new_refresh_token),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
            expires_at=new_refresh_expires_at,
            tid=new_token_id,
        )

        db.commit()
    except (AppException, IntegrityError):
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise sign_in_failed_error()

    return SignInServiceResult(
        user_id=user.id,
        refresh_token=new_refresh_token,
        access_token=create_access_token(user_id=user.id),
    )


def refresh_user(
    payload: RefreshPayload, request: Request, db: Session
) -> RefreshServiceResult:
    try:
        token_id, user_id = parse_refresh_token_ids(payload.refresh_token)
        user_session = get_valid_user_session(
            db=db,
            refresh_token=payload.refresh_token,
            user_id=user_id,
            token_id=token_id,
        )

        user_session.revoked_at = datetime.now(UTC)

        new_token_id = uuid.uuid4()
        new_refresh_token = create_refresh_token(
            user_id=user_session.user_id,
            token_id=new_token_id,
        )
        new_refresh_expires_at = get_refresh_token_expires_at()
        create_user_session(
            db=db,
            user_id=user_session.user_id,
            refresh_token_hash=hash_password(new_refresh_token),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
            expires_at=new_refresh_expires_at,
            tid=new_token_id,
        )

        db.commit()
    except ValueError:
        db.rollback()
        raise invalid_refresh_token_error()
    except (AppException, IntegrityError):
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise refresh_failed_error()

    return RefreshServiceResult(
        user_id=user_session.user_id,
        refresh_token=new_refresh_token,
        access_token=create_access_token(user_id=user_session.user_id),
    )


def logout_user(payload: LogoutPayload, db: Session) -> None:
    try:
        token_id, _user_id = parse_refresh_token_ids(payload.refresh_token)
        user_session = get_user_session_by_token_id(db=db, token_id=token_id)

        if (
            not user_session
            or user_session.revoked_at is not None
            or user_session.expires_at <= datetime.now(UTC)
        ):
            return None

        user_session.revoked_at = datetime.now(UTC)
        db.commit()
        return None
    except (AppException, ValueError):
        db.rollback()
        return None
