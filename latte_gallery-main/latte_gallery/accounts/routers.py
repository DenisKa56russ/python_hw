from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.params import Depends
from pydantic import PositiveInt
from passlib.hash import pbkdf2_sha256 as plh
from datetime import timedelta

from latte_gallery.accounts.schemas import (
    AccountCreateSchema,
    AccountPasswordUpdateSchema,
    AccountRegisterSchema,
    AccountSchema,
    AccountUpdateSchema,
    Role,
)
from latte_gallery.core.dependencies import AccountServiceDep, SessionDep
from latte_gallery.core.schemas import Page, PageNumber, PageSize, Token
from latte_gallery.security.dependencies import (AuthenticatedAccount, AuthorizedAccount,
                                                 create_access_token, authenticate_by_token)
from latte_gallery.security.permissions import Anonymous, Authenticated, IsAdmin

accounts_router = APIRouter(prefix="/accounts", tags=["Аккаунты"])


@accounts_router.post(
"/token",
    summary="Создать токен",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthorizedAccount(Authenticated()))],
)
async def login_for_access_token(account: AuthenticatedAccount, response: Response) -> Token:
    access_token_expires = timedelta(minutes=30)
    access_token = await create_access_token(
        data={"sub": account.login, "pas":account.password}, expires_delta=access_token_expires
    )
    response.set_cookie(key="jwt-token", value=access_token)
    return Token(access_token=access_token, token_type="bearer")


@accounts_router.get(
"/authenticate",
    summary="Аутентификация по куки",
    status_code=status.HTTP_202_ACCEPTED,
)
async def authenticate_by_cookie(request: Request, account_service: AccountServiceDep, session: SessionDep):
    cookie_token = request.cookies.get('jwt-token')
    account = await authenticate_by_token(cookie_token, account_service, session)
    if not account:
        raise HTTPException(404)
    return account


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
            password=plh.hash(body.password),
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

    body.password = plh.hash(body.password)

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
async def get_account_by_id(
        id: PositiveInt, account_service: AccountServiceDep, session: SessionDep
) -> AccountSchema:
    return await account_service.find_by_id(id, session)


@accounts_router.get("", summary="Получить список всех аккаунтов")
async def get_all_accounts(
        page: PageNumber, size: PageSize,
        account_service: AccountServiceDep, session: SessionDep
) -> Page[AccountSchema]:
    return await account_service.find_all(page, size, session)


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
        id: PositiveInt, body: AccountUpdateSchema, account_service: AccountServiceDep, session: SessionDep
) -> AccountSchema:
    return await account_service.update_by_id(id, body, session)