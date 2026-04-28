from fastapi import Request, Response

from app.services.errors.auth import (
    invalid_refresh_token_error,
)

REFRESH_TOKEN_COOKIE_KEY = "refresh_token"
REFRESH_TOKEN_COOKIE_MAX_AGE = 60 * 60 * 24 * 7

def get_refresh_token_from_cookie(request: Request) -> str:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_KEY)
    if not refresh_token:
        raise invalid_refresh_token_error()
    return refresh_token


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=REFRESH_TOKEN_COOKIE_MAX_AGE,
    )


def clear_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
    )
