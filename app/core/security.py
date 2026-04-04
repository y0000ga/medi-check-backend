import uuid
from datetime import UTC, datetime, timedelta
from fastapi import Request
from passlib.context import CryptContext
from jose import JWTError, ExpiredSignatureError, jwt

from typing import Any

from app.services.errors.auth import (
    expired_refresh_token_error,
    invalid_refresh_token_error,
)
from app.services.errors.user import (
    expired_access_token_error,
    invalid_access_token_error,
)

# 不使用 sha256 的原因是因為 bcrypt (專門 for 密碼) 比較安全
# 建立密碼雜湊設定。
# 這裡指定使用 bcrypt，之後 hash 與 verify 都透過同一個 context 處理。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

REFRESH_SECRET_KEY = "your-secret-key"
REFRESH_TOKEN_EXPIRE_DAYS = 7

ACCESS_SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


# 註冊時使用
def hash_password(password: str) -> str:
    # 將使用者輸入的原始密碼轉成安全的雜湊字串，
    # 存進資料庫時應該存這個結果，不要直接存原始密碼。
    return pwd_context.hash(password)


# 登入時使用
def verify_password(password: str, password_hash: str) -> bool:
    # 驗證登入時輸入的原始密碼，
    # 是否和資料庫中已儲存的 password_hash 相符。
    return pwd_context.verify(password, password_hash)


# 產生長效 token 的過期時間
def get_refresh_token_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)


# 產生長效 token
def create_refresh_token(user_id: uuid.UUID, token_id: uuid.UUID) -> str:
    expire = get_refresh_token_expires_at()

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tid": str(token_id),
        "exp": expire,
    }

    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


# 解開長效 token
def decode_refresh_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise expired_refresh_token_error()
    except JWTError:
        raise invalid_refresh_token_error()


# 解析 refresh_token 內容
def parse_refresh_token_ids(token: str) -> tuple[uuid.UUID, uuid.UUID]:
    try:
        payload = decode_refresh_token(token)

        tid = payload.get("tid")
        sub = payload.get("sub")

        if not tid or not sub:
            raise invalid_refresh_token_error()
        return uuid.UUID(tid), uuid.UUID(sub)
    except ValueError:
        raise invalid_refresh_token_error()

def get_access_token_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# 產生短時間 token
def create_access_token(user_id: uuid.UUID) -> str:
    expire = get_access_token_expires_at()
    payload: dict[str, Any] = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)


# 解開短時間 token
def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise expired_access_token_error()
    except JWTError:
        raise invalid_access_token_error()


# 解析 access_token 內容
def parse_access_token_user_id(token: str) -> uuid.UUID:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")

        if not sub:
            raise invalid_access_token_error()

        return uuid.UUID(sub)
    except ValueError:
        raise invalid_access_token_error()

def get_bearer_token_from_header(request: Request) -> str:
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise Exception("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise Exception("Invalid Authorization header")

    return token
