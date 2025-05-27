from fastapi import (
    Body, 
    HTTPException, 
    status,
    Request
)
from fastapi.responses import JSONResponse
from utils.logger import logger
from orm.mongodb.managament.api_gateway import ManageAPIGateway
from orm.postgresql.managament.white_list_urls import ManageWhiteListUrls


async def validate_data_from_create(body = Body()):
    logger.debug(body)
    required_keys = [
        "main_api", 
        "first_api_response",
        "first_api_percent",
        "second_api_response",
        "second_api_percent",
    ]
    if all(key in body for key in required_keys):
        logger.debug("Проверка успешно пройдена")
        return body
    logger.debug("Проверка не пройдена")
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE, 
        detail="incorrect data"
    )

async def get_settings_url(request: Request) -> dict:
    id_user = request.state.payload["sub"]
    api_gateway = ManageAPIGateway(id_user)
    data_from_redirect_bytes: tuple = request.scope.get("headers")[-2]
    url = data_from_redirect_bytes[1].decode()
    settings_url = await api_gateway.get(url)
    return settings_url

async def check_url_in_white_list(request: Request) -> str:
    data_from_redirect_bytes: tuple = request.scope.get("headers")[-2]
    element: bytes = data_from_redirect_bytes[0].decode()
    logger.debug(element)
    if element != "referer":
        return JSONResponse(
            content="bad request",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    url = data_from_redirect_bytes[1].decode()
    check_url = await ManageWhiteListUrls.get(url)
    if not check_url:
        return JSONResponse(
            content="main api invalid",
            status_code=status.HTTP_400_BAD_REQUEST
        ) 
    return check_url