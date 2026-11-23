from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestFormStrict

from src.api.auth.dependencies import token_form_dependency
from src.api.auth.dto import (
    CurrentUserOut,
    RegisterIn,
    TokenErrorOut,
    TokenOut,
)
from src.api.auth.exceptions import InvalidCredentials
from src.api.auth.service import AuthServiceDep
from src.dependencies.auth import CurrentUserDep

router = APIRouter(tags=["auth"], prefix="/auth")

INVALID_CREDENTIALS_RESPONSE = {
    "error": "invalid_grant",
    "error_description": "Username or password is invalid",
}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_class=Response,
    responses={status.HTTP_409_CONFLICT: {"description": "Username already exists"}},
)
async def register(
    user: Annotated[RegisterIn, Body()], auth_service: AuthServiceDep
) -> None:
    await auth_service.register(user)


@router.get(
    "/me",
    response_model=CurrentUserOut,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid bearer token"
        },
    },
)
async def get_profile(user: CurrentUserDep, auth_service: AuthServiceDep) -> Any:
    return await auth_service.get_profile(id=user.id)


@router.post(
    "/token",
    dependencies=[token_form_dependency],
    response_model=TokenOut,
    responses={
        200: {
            "headers": {
                "Cache-Control": {"schema": {"type": "string", "const": "no-store"}},
                "Pragma": {"schema": {"type": "string", "const": "no-cache"}},
            }
        },
        400: {"model": TokenErrorOut, "description": "OAuth token request error"},
    },
    description="Token lifetime is configured by ACCESS_TOKEN_EXPIRE_MINUTES.",
)
async def login(
    credentials: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    response: Response,
    auth_service: AuthServiceDep,
) -> TokenOut | JSONResponse:
    try:
        token = await auth_service.login(
            username=credentials.username, password=credentials.password
        )
    except InvalidCredentials:
        return JSONResponse(status_code=400, content=INVALID_CREDENTIALS_RESPONSE)

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return token
