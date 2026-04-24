import uuid

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from datetime import UTC, datetime
from sqlalchemy.orm import Session

from app.schemas.auth import (
    SignUpPayload,
    SignUpServiceResult,
    SignInPayload,
    SignInServiceResult,
    RefreshServiceResult,
    RefreshPayload,
    LogoutPayload,
)

from app.core.security import (
    hash_password,
    create_refresh_token,
    get_refresh_token_expires_at,
    create_access_token,
    parse_refresh_token_ids,
    verify_password,
)
from app.core.exceptions import AppException

from app.repositories.user import get_user_by_email, create_user
from app.repositories.patient import create_patient_for_user
from app.repositories.user_session import (
    create_user_session,
    delete_inactive_sessions_by_user_id,
    get_user_session_by_token_id,
)

from app.services.errors.auth import (
    refresh_failed_error,
    invalid_refresh_token_error,
    sign_in_failed_error,
    invalid_credentials_error,
    sign_up_failed_error,
    duplicate_email_error,
)
from app.validation.rules import NAME_RULE, PASSWORD_RULE
from app.core.validators import validate_required_string_field
from app.services.validators.auth import get_valid_user_session
from app.services.validators.user import validate_active_user


def sign_up_user(
    payload: SignUpPayload, request: Request, db: Session
) -> SignUpServiceResult:
    try:
        # 1. email 不可重複
        normalized_email = payload.email.strip().lower()
        existing_user = get_user_by_email(db=db, email=normalized_email)
        if existing_user:
            raise duplicate_email_error()
        # 2. password hash

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

        hashed_password = hash_password(normalized_password)

        # 3. create user object
        user = create_user(
            db=db,
            email=normalized_email,
            name=normalized_name,
            password_hash=hashed_password,
        )

        # 4. create patient(linked_user_id=user.id, name=user.name) object
        create_patient_for_user(db=db, user_id=user.id, name=user.name)

        # 5. create user session
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

        # 6. commit -> 真的存進 DB 了
        # 要想如果失敗怎麼辦?
        # email 唯一鍵撞到
        # 某欄位資料不合法
        # DB transaction 失敗
        # 出錯就撤回 by rollback，不然會導致 session 的 transaction 狀態壞掉
        # db.add 時只會把 obj 放到 session，真正送到 DB 是在 flush() 或 commit()
        db.commit()
    except AppException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        error_message = str(exc.orig).lower()
        if "unique constraint failed: users.email" in error_message:
            raise duplicate_email_error()
        raise
    except Exception:
        db.rollback()
        raise sign_up_failed_error()
    # 7. return response
    return SignUpServiceResult(
        user_id=user.id,
        refresh_token=new_refresh_token,
        access_token=create_access_token(user_id=user.id),
    )


def sign_in_user(
    payload: SignInPayload, request: Request, db: Session
) -> SignInServiceResult:
    try:
        # normalize email
        normalized_email = payload.email.strip().lower()

        # 用 email 找 user
        current_user = get_user_by_email(db=db, email=normalized_email)
        user = validate_active_user(user=current_user)

        # 驗證 Password
        is_valid_password = verify_password(payload.password, user.password_hash)

        # Password 驗證失敗
        if not is_valid_password:
            raise invalid_credentials_error()

        # delete revoked, expired sessions
        delete_inactive_sessions_by_user_id(user_id=user.id, db=db)
        # 產生 refresh_token 並建立 UserSession
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

        # commit
        db.commit()
        # 回 user_id + access_token + refresh_token
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
        # 查出這個 token 對應的有效 UserSession
        token_id, user_id = parse_refresh_token_ids(payload.refresh_token)
        user_session = get_valid_user_session(
            db=db,
            refresh_token=payload.refresh_token,
            user_id=user_id,
            token_id=token_id,
        )
        now = datetime.now(UTC)
        # 先把舊 session 作廢
        user_session.revoked_at = now
        # 產生新的 refresh_token
        new_token_id = uuid.uuid4()
        new_refresh_token = create_refresh_token(
            user_id=user_session.user_id,
            token_id=new_token_id,
        )
        new_refresh_expires_at = get_refresh_token_expires_at()
        # 更新原 session 或建立新 session
        create_user_session(
            db=db,
            user_id=user_session.user_id,
            refresh_token_hash=hash_password(new_refresh_token),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
            expires_at=new_refresh_expires_at,
            tid=new_token_id,
        )
        # commit
        db.commit()
        # 回傳新的 tokens
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
        # 查出這個 token 對應的有效 UserSession
        token_id, _user_id = parse_refresh_token_ids(payload.refresh_token)
        user_session = get_user_session_by_token_id(db=db, token_id=token_id)

        if not user_session or user_session.revoked_at:
            return None

        user_session.revoked_at = datetime.now(UTC)

        db.commit()
        return None
    except AppException:
        db.rollback()
        return None


