from fastapi import (
    Request, status
)
from utils.logger import logger
from fastapi.responses import JSONResponse
from orm.postgresql.managament.white_list_urls import ManageWhiteListUrls
from orm.postgresql.models import WhiteListUrls
from typing import Union


async def check_redirect(request: Request) -> Union[WhiteListUrls, JSONResponse]:
    '''
    Проверяет, был ли запрос redirect. 
    Если это был прямой запрос, то вернёт ответ со статусом 400,
    если нет, то вернёт объект WhiteListUrls.

    Params:
        request: Запрос.
    :return WhiteListUrls | JSONResponse: 
    Вернёт WhiteListUrls, если проверка была пройдена, иначе JSONResponse.
    '''
    data_from_redirect_bytes: tuple = request.scope.get("headers")[-2]
    element: bytes = data_from_redirect_bytes[0].decode()
    logger.debug(element)
    if element != "referer":
        return JSONResponse(
            content="bad request",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    url = data_from_redirect_bytes[1].decode()
    obj_url = await ManageWhiteListUrls.get(url)
    if not obj_url:
        return JSONResponse(
            content="main api invalid",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return obj_url

