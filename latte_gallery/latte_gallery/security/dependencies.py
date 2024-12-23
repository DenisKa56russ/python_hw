from typing import Annotated
import jwt

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

from latte_gallery.accounts.models import Account
from latte_gallery.core.dependencies import AccountServiceDep, SessionDep
from latte_gallery.security.permissions import BasePermission

SecuritySchema = HTTPBearer(auto_error=False)


async def authenticate_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(SecuritySchema)],
    account_service: AccountServiceDep,
    session: SessionDep,
):
    if credentials is None:
        return None
    data = jwt.decode(credentials.credentials, "secret", algorithms="HS256")
    return await account_service.authorize(
        data["login"], data["password"], session
    )


AuthenticatedAccount = Annotated[Account | None, Depends(authenticate_user)]


class AuthorizedAccount:
    def __init__(self, permission: BasePermission):
        self._permission = permission

    def __call__(self, account: AuthenticatedAccount):
        if not self._permission.check_permission(account):
            raise HTTPException(status.HTTP_403_FORBIDDEN)
