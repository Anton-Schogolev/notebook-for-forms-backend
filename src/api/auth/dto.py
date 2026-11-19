from pydantic import BaseModel


class LoginIn(BaseModel):
    """TODO: define the credentials accepted by the login endpoint."""


class TokenOut(BaseModel):
    """TODO: define the token fields exposed in API responses."""
