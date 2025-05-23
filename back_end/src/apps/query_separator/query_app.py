from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Request,
    HTTPException, status,
    Depends, 
)
from fastapi.responses import JSONResponse, RedirectResponse
from utils.logger import logger
from fastapi import FastAPI, Request
from orm.postgresql.managament.white_list_urls import ManageWhiteListUrls
from orm.mongodb.managament.api_gateway import ManageAPIGateway
import time
import random
import aiohttp
from json import loads

app = FastAPI()


@app.middleware("http")
async def check_url_in_white_list(
    request: Request,
    call_next: callable
):
    data_from_redirect_bytes: tuple = request.scope.get("headers")[-2]
    element: bytes = data_from_redirect_bytes[0].decode()
    logger.debug(element)
    if element != "referer":
        return JSONResponse(
            content="bad request",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    url = data_from_redirect_bytes[1].decode()
    obj = await ManageWhiteListUrls.get(url)
    if not obj:
        return JSONResponse(
            content="main api invalid",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    request.state.id_user = obj.user_id
    request.state.main_api = url
    response = await call_next(request) # исправить для GET
    return response

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter() - start_time
    logger.debug(end_time)
    return response


@app.post("/query_separator")
@app.get("/query_separator")
async def query_separator(
    request: Request, 
    # settings_url: dict = Depends(get_settings_url)
):  
    id_user = request.state.id_user
    main_api = request.state.main_api

    api_gateway = ManageAPIGateway(str(id_user))
    settings_url = await api_gateway.get(main_api)
    current_url_number = random.randrange(0, 2)
    match current_url_number:
        case 0:
            response_url = settings_url["first_api_response"]
            # функция для обработки данных
        case 1:
            response_url = settings_url["second_api_response"]
            # функция для обработки данных
    async with aiohttp.ClientSession() as session:
        async with session.get(url=response_url) as response:
            response_text = await response.text()
 
    return loads(response_text)
    # return RedirectResponse(response_url)