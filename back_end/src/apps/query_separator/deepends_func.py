from fastapi import (
    Request, status
)
from utils.logger import logger
from fastapi.responses import JSONResponse
from orm.postgresql.managament.white_list_urls import ManageWhiteListUrls



async def check_redirect(request: Request):
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

