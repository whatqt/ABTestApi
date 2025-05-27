from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Request,
    HTTPException, status,
    Depends, BackgroundTasks
)
from fastapi.responses import JSONResponse
from utils.logger import logger
from fastapi import FastAPI, Request
from orm.postgresql.managament.white_list_urls import ManageWhiteListUrls
from orm.postgresql.models import WhiteListUrls
from orm.mongodb.managament.api_gateway import ManageAPIGateway, SaveCollections
import time
import random
import aiohttp
from json import loads
from .deepends_func import check_redirect



app = FastAPI()


@app.middleware("http")
async def check_url_in_white_list(
    request: Request,
    call_next: callable
):
    obj_url = await check_redirect(request)
    if isinstance(obj_url, WhiteListUrls):
        request.state.id_user = obj_url.user_id
        request.state.main_api = obj_url.url
        response = await call_next(request) # исправить для GET
        return response
    return obj_url

async def save_time_request(
    id_user,
    main_api,
    time_,
    response_url
):
    save_collection = SaveCollections(id_user)
    await save_collection.save_time_request(
        main_api,
        time_,
        response_url
    )
    logger.debug("latency был сохранён")


@app.post("/query_separator")
@app.get("/query_separator")
async def query_separator(
    request: Request, 
    back_task: BackgroundTasks
):  
    id_user = str(request.state.id_user)
    main_api = request.state.main_api
    api_gateway = ManageAPIGateway(id_user)
    settings_url = await api_gateway.get(main_api)
    current_url_number = random.randrange(0, 2)
    match current_url_number:
        case 0:
            response_url = settings_url["first_api_response"]
        case 1:
            response_url = settings_url["second_api_response"]
    start_time = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=response_url) as response:
            response_text = await response.text()
    end_time = time.perf_counter() - start_time
    back_task.add_task(
        save_time_request,
        id_user,
        main_api,
        end_time,
        response_url
    )
    return loads(response_text)
