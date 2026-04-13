from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.response import error_response
from app.schemas.base import ValidationErrorDetail


def register_exception_handlers(app: FastAPI) -> None:
    def json_error_response(
        status_code: int,
        message: str,
        details: list[ValidationErrorDetail] | None = None,
    ) -> JSONResponse:
        payload = error_response(
            status_code=status_code,
            message=message,
            details=details,
        )
        return JSONResponse(
            status_code=status_code,
            content=payload.model_dump(),
        )

    # 只要程式裡有人 raise AppException，
    # 就交給這個 handler 統一處理成固定格式的回應
    @app.exception_handler(AppException)
    async def _(request: Request, exc: AppException):
        return json_error_response(
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(IntegrityError)
    async def _(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "statusCode": 400,
                    "message": "Database integrity error",
                    "details": [],
                },
                "data": None,
            },
        )

    # 處理 request schema 驗證失敗，例如缺欄位、型別錯、EmailStr 格式錯
    @app.exception_handler(RequestValidationError)
    async def _(request: Request, exc: RequestValidationError):
        details: list[ValidationErrorDetail] = []

        # exc.errors() 是 list of error
        for err in exc.errors():
            loc = err.get("loc", [])  # 有 loc 就拿，沒有就用 [] 作為預設值
            # 排除 body，因為 body 只是 FastAPI 告訴你錯誤來自 request body
            field = ".".join(str(item) for item in loc if item != "body")
            details.append(
                ValidationErrorDetail(
                    field=field,
                    message=err.get("msg", "Invalid value"),
                    type=err.get("type", "validation_error"),
                )
            )

        return json_error_response(
            status_code=422,
            message="Request validation failed",
            details=details,
        )

    @app.exception_handler(HTTPException)
    async def _(request: Request, exc: HTTPException):
        return json_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
        )

    @app.exception_handler(Exception)
    async def _(_request: Request, _exc: Exception):
        return json_error_response(
            status_code=500,
            message="Internal server error",
        )
