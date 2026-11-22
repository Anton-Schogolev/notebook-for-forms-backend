from typing import Any

from fastapi import Request, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.auth.exceptions import JWTException
from src.api.auth.router import login
from src.api.user.exceptions import UsernameAlreadyTaken


async def handle_username_taken(
    _request: Request, _exc: UsernameAlreadyTaken
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "Username is already taken"},
    )


async def handle_jwt_exception(_request: Request, _exc: JWTException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid bearer token"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_request_validation(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    if request.scope.get("endpoint") is not login:
        return await request_validation_exception_handler(request, exc)

    unsupported_grant = any(
        error["loc"] == ("body", "grant_type")
        and error["type"] == "string_pattern_mismatch"
        for error in exc.errors()
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "unsupported_grant_type"
            if unsupported_grant
            else "invalid_request"
        },
    )


# It's nigh impossible to type this dict so each key matches its handler's exception type.
EXCEPTION_HANDLERS: Any = {
    RequestValidationError: handle_request_validation,
    UsernameAlreadyTaken: handle_username_taken,
    JWTException: handle_jwt_exception,
}
