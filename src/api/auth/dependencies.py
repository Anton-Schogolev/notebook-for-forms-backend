from fastapi import Depends, Request
from fastapi.exceptions import RequestValidationError


async def validate_token_form(request: Request) -> None:
    media_type = (
        request.headers.get("content-type", "").partition(";")[0].strip().lower()
    )
    if media_type != "application/x-www-form-urlencoded":
        raise RequestValidationError(
            [
                {
                    "loc": ("header", "content-type"),
                    "type": "value_error",
                    "msg": "Expected URL-encoded form data",
                }
            ]
        )

    form = await request.form()
    if len(form.multi_items()) != len(form):
        raise RequestValidationError(
            [
                {
                    "loc": ("body",),
                    "type": "value_error",
                    "msg": "Repeated form parameter",
                }
            ]
        )


token_form_dependency = Depends(validate_token_form)
