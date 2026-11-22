class InvalidCredentials(Exception):
    """The supplied username or password is invalid."""


class JWTException(Exception):
    """The bearer token is invalid."""
