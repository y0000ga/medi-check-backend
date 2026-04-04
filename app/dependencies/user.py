import uuid

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.security import get_bearer_token_from_header, parse_access_token_user_id
from app.db.session import get_db
from app.repositories.user import get_user_by_id
from app.services.validators.user import validate_active_user


def get_current_user_id(request: Request):
    # 從 request 取 access_token
    access_token = get_bearer_token_from_header(request=request)
    # 驗證 access_token
    user_id = parse_access_token_user_id(token=access_token)
    # 解析出 current_user_id
    return user_id



def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    current_user = get_user_by_id(db=db, user_id=user_id)
    return validate_active_user(current_user)
