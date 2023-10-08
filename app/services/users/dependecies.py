from datetime import datetime

from fastapi import Request, Depends
from jose import jwt, JWTError

from app.config import settings
from app.exceptions import (TokenExpiredException, TokenAbsentException, IncorrectTokenFormatException,
                            UserIsNotPresentException)
from app.services.users.dao import UsersDaO
from app.models.users import Users


def get_token(request: Request) -> str:
    token = request.cookies.get('clinic_access_token')
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)) -> Users:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, settings.JWT_ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException

    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDaO.get_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user
