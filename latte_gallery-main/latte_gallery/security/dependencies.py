from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPBasic, HTTPBasicCredentials

from latte_gallery.accounts.models import Account
from latte_gallery.core.dependencies import AccountServiceDep, SessionDep
from latte_gallery.security.permissions import BasePermission
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.settings import settings
from accounts.schemas import User
from accounts.services import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/login")  # Modify if login path is different

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int) -> str:
    to_encode = data.copy()
    # expires in seconds
    to_encode["exp"] = expires_delta
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends()]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await user_service.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends()]
) -> Optional[User]:
    if not token:
        return None

    try:
       payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
       email: str = payload.get("sub")
       if email is None:
           return None
    except JWTError:
       return None
    user = await user_service.get_user_by_email(email=email)
    return user
SecuritySchema = HTTPBasic(auto_error=False)


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


AuthenticatedAccount = Annotated[Account | None, Depends(authenticate_user)]


class AuthorizedAccount:
    def __init__(self, permission: BasePermission):
        self._permission = permission

    def __call__(self, account: AuthenticatedAccount):
        if not self._permission.check_permission(account):
            raise HTTPException(status.HTTP_403_FORBIDDEN)
