from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from fastapi.security import (
    OAuth2PasswordRequestFormStrict,
)

from src.api.auth.dto import CurrentUserOut, RegisterIn, TokenOut
from src.dependencies.auth import CurrentUserDep

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: Annotated[RegisterIn, Body()]) -> None:
    pass


@router.get("/me", response_model=CurrentUserOut)
def get_profile(user: CurrentUserDep) -> Any:
    pass


@router.post(
    "/token",
    description=("The `scope`, `client_id`, and `client_secret` fields are ignored."),
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
) -> TokenOut:
    # user_dict = fake_users_db.get(form_data.username)
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # return {"access_token": user.username, "token_type": "bearer"}
    return TokenOut(access_token="placeholder", token_type="bearer")
