from fastapi import Request
from fastapi.responses import RedirectResponse

from app.models import User
from app.services.auth import get_current_user


async def optional_user(request: Request) -> User | None:
    return await get_current_user(request)


def login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)
