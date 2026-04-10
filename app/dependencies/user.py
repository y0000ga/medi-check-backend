import uuid

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import bearer_scheme, parse_access_token_user_id
from app.db.session import get_db
from app.repositories.user import get_user_by_id
from app.services.errors.user import invalid_access_token_error
from app.services.validators.user import validate_active_user


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> uuid.UUID:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise invalid_access_token_error()

    return parse_access_token_user_id(token=credentials.credentials)


def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    current_user = get_user_by_id(db=db, user_id=user_id)
    return validate_active_user(current_user)
