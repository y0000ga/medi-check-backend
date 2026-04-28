from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    SignUpBody,
    SignUpPayload,
    SignUpResponse,
    SignInPayload,
    SignInBody,
    SignInResponse,
    RefreshPayload,
    RefreshResponse,
    LogoutPayload,
)
from app.schemas.base import ApiResponse
from app.core.response import success_response
from app.services.auth import sign_up_user, sign_in_user, refresh_user, logout_user
router = APIRouter(prefix="/auth", tags=["auth"])


# 登入
# 後端回：
# access_token 前端之後呼叫一般 API 時帶 access_token
# refresh_token
@router.post("/sign-in")
def sign_in(
    body: SignInBody,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[SignInResponse]:
    payload = SignInPayload(email=body.email, password=body.password)

    result = sign_in_user(payload=payload, request=request, db=db)

    sign_in_response = SignInResponse(
        user_id=result.user_id,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )
    return success_response(sign_in_response)


# payload - request body 解析後的資料
# request - FastAPI 注入的 HTTP request 物件
# db -
# 透過 dependency 注入的資料庫 session
# 這個 route 需要一個 DB session，請 FastAPI 幫我從 get_db() 拿
# 註冊
@router.post("/sign-up")
def sign_up(
    body: SignUpBody,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[SignUpResponse]:
    payload = SignUpPayload(
        name=body.name,
        birth_date=body.birth_date,
        password=body.password,
        email=body.email,
    )

    result = sign_up_user(payload=payload, request=request, db=db)

    sign_up_response = SignUpResponse(
        user_id=result.user_id,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

    return success_response(sign_up_response)


# access_token 過期後，前端拿 refresh_token 去 /auth/refresh
# 後端查 user_sessions.refresh_token_hash，合法才發新的 access_token
@router.post("/refresh")
def refresh(
    payload: RefreshPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[RefreshResponse]:
    result = refresh_user(payload=payload, request=request, db=db)

    refresh_response = RefreshResponse(
        user_id=result.user_id,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

    return success_response(refresh_response)


# 登出
@router.post("/logout")
def logout(
    payload: LogoutPayload,
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    logout_user(payload=payload, db=db)

    return success_response(None)

# 忘記密碼
@router.post("/forgot-password")
def forgot_password():
    return success_response(None)

# 重設密碼
@router.post("/reset-password")
def reset_password():
    return success_response(None)
