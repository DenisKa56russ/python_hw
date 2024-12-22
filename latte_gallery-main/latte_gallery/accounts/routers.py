from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from pydantic import PositiveInt

from latte_gallery.accounts.schemas import (
    AccountCreateSchema,
    AccountPasswordUpdateSchema,
    AccountRegisterSchema,
    AccountSchema,
    AccountUpdateSchema,
    Role,
)
from latte_gallery.core.dependencies import AccountServiceDep, SessionDep
from latte_gallery.core.schemas import Page, PageNumber, PageSize
from latte_gallery.security.dependencies import AuthenticatedAccount, AuthorizedAccount
from latte_gallery.security.permissions import Anonymous, Authenticated, IsAdmin
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from core.settings import settings
from accounts import schemas, services
from security.dependencies import create_access_token

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/register", response_model=schemas.User)
async def register_user(
    user_create: schemas.UserCreate, user_service: Annotated[services.UserService, Depends()]
):
    return await user_service.create_user(user_create)

@router.post("/login")
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[services.UserService, Depends()]
):
    user = await user_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.email}, expires_delta=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
async def get_current_user(
    current_user: Annotated[schemas.User, Depends(services.get_current_user)]
):
   return current_user
accounts_router = APIRouter(prefix="/accounts", tags=["Аккаунты"])


@accounts_router.post(
    "/register",
    summary="Регистрация нового аккаунта",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthorizedAccount(Anonymous()))],
)
async def register_account(
    body: AccountRegisterSchema, account_service: AccountServiceDep, session: SessionDep
) -> AccountSchema:
    account = await account_service.create(
        AccountCreateSchema(
            login=body.login,
            password=body.password,
            name=body.name,
            role=Role.USER,
        ),
        session,
    )

    return AccountSchema.model_validate(account)


@accounts_router.post(
    "",
    summary="Создать новый аккаунт",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthorizedAccount(IsAdmin()))],
)
async def create_account(
    body: AccountCreateSchema,
    current_user: AuthenticatedAccount,
    account_service: AccountServiceDep,
    session: SessionDep,
) -> AccountSchema:
    assert current_user is not None

    if (current_user.role == Role.MAIN_ADMIN and body.role == Role.MAIN_ADMIN) or (
        current_user.role == Role.ADMIN and body.role in {Role.ADMIN, Role.MAIN_ADMIN}
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    account = await account_service.create(body, session)

    return AccountSchema.model_validate(account)


@accounts_router.get(
    "/my",
    summary="Получение данных своего аккаунта",
    dependencies=[Depends(AuthorizedAccount(Authenticated()))],
)
async def get_my_account(account: AuthenticatedAccount) -> AccountSchema:
    return AccountSchema.model_validate(account)


@accounts_router.get("/{id}", summary="Получение аккаунт по идентификатору")
async def get_account_by_id(id: PositiveInt) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.get("", summary="Получить список всех аккаунтов")
async def get_all_accounts(
    page: PageNumber = 0, size: PageSize = 10
) -> Page[AccountSchema]:
    return Page(
        count=1,
        items=[
            AccountSchema(
                id=1, login="owner", name="Петр Иванов", role=Role.MAIN_ADMIN
            ),
            AccountSchema(id=1, login="admin", name="Иван Петров", role=Role.ADMIN),
            AccountSchema(id=3, login="user1", name="Вася Пупкин", role=Role.USER),
        ],
    )


@accounts_router.put("/my", summary="Обновление данных своего аккаунта")
async def update_my_account(body: AccountUpdateSchema) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.put("/my/password", summary="Обновить пароль своего аккаунта")
async def update_my_account_password(
    body: AccountPasswordUpdateSchema,
) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.put("/{id}", summary="Обновить аккаунт по идентификатору")
async def update_account_by_id(
    id: PositiveInt, body: AccountUpdateSchema
) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )
