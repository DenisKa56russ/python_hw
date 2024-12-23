import os
import jwt
from datetime import datetime, timezone, timedelta
from typing import Annotated
from dotenv import load_dotenv

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPBasic, HTTPBasicCredentials

from latte_gallery.accounts.models import Account
from latte_gallery.core.dependencies import AccountServiceDep, SessionDep
from latte_gallery.security.permissions import BasePermission


SecuritySchema = HTTPBasic(auto_error=False)
load_dotenv()
TOKEN_SECRET = os.getenv('TOKEN_SECRET')


async def authenticate_user(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(SecuritySchema)],
    account_service: AccountServiceDep,
    session: SessionDep,
):
    if credentials is None:
        return None

    return await account_service.authorize(
        credentials.username, credentials.password, session
    )


async def authenticate_by_token(
    token: str,
    account_service: AccountServiceDep,
    session: SessionDep,
):
    if token is None:
        return None
    user_data = jwt.decode(token, str(TOKEN_SECRET), algorithms=["HS256"])

    return await account_service.authorize(
        user_data['sub'], user_data['pas'], session
    )

    # return user_data


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(TOKEN_SECRET), algorithm="HS256")
    return encoded_jwt


AuthenticatedAccount = Annotated[Account | None, Depends(authenticate_user)]


class AuthorizedAccount:
    def __init__(self, permission: BasePermission):
        self._permission = permission

    def __call__(self, account: AuthenticatedAccount):
        if not self._permission.check_permission(account):
            raise HTTPException(status.HTTP_403_FORBIDDEN)