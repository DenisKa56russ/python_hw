from fastapi import APIRouter
import jwt

from latte_gallery.core.dependencies import SessionDep
from latte_gallery.core.schemas import StatusResponse
from latte_gallery.accounts.schemas import ForToken

status_router = APIRouter(prefix="/status")
jwt_router = APIRouter(prefix="/token")

@jwt_router.post("", summary="Получение токена", tags=["Токен"])
def token(body: ForToken):
    login = body.login
    password = body.password
    token = jwt.encode({"login":login,"password": password}, "secret", algorithm="HS256")
    return token

@status_router.get("", summary="Получить статус сервера", tags=["Статус"])
def get_status(session: SessionDep) -> StatusResponse:
    return StatusResponse(status="ok")
