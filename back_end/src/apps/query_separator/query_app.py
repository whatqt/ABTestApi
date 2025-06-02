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
from orm.mongodb.managament.api_gateway import ManageAPIGateway, SaveStatistics
import time
import random
import aiohttp
from json import loads
from .deepends_func import check_redirect
import psutil
import tracemalloc



app = FastAPI()


@app.middleware("http")
async def check_url_in_white_list(
    request: Request,
    call_next: callable
):
    '''
    проверяет, была ли переадрисация от допустимого URL. 
    Если да, то вернёт объект WhiteListUrls. Иначе вернёт ошибку.
    '''
    obj_url = await check_redirect(request)
    if isinstance(obj_url, WhiteListUrls):
        request.state.id_user = obj_url.user_id
        request.state.main_api = obj_url.url
        response = await call_next(request) # исправить для GET
        return response
    return obj_url

async def save_time_request(
    id_user: str,
    main_api: str,
    time_: float,
    response_url: str
):
    '''
    Сохраняет время запроса.
    
    Params:
        id_user: Id пользователя.
        main_api: Url, с которого был отправлен запрос.
        time_: Время запроса.
        response_url: Какой url обработал.
    '''
    save_collection = SaveStatistics(
        id_user, main_api
    )
    await save_collection.save_time_request(
        time_,
        response_url
    )
    logger.debug("latency был сохранён")

async def save_memory(
    id_user: str,
    main_api: str,
    memory: int,
    response_url: str
):
    '''
    Сохраняет время запроса.
    
    Params:
        id_user: Id пользователя.
        main_api: Url, с которого был отправлен запрос.
        memory: Память, которая была затрачена на запрос.
        response_url: Какой url обработал.
    '''
    save_collection = SaveStatistics(
        id_user, main_api
    )
    await save_collection.save_memory(
        memory,
        response_url
    )
    logger.debug("кол-во использованной памяти было сохранено")
    
async def save_busyness_cpu(
    id_user: str,
    main_api: str,
    value: int,
    response_url: str
):
    '''
    Сохраняет время запроса.
    
    Params:
        id_user: Id пользователя.
        main_api: Url, с которого был отправлен запрос.
        value: Сколько было затрачено процессора во время запроса.
        response_url: Какой url обработал.
    '''
    save_collection = SaveStatistics(
        id_user, main_api
    )
    await save_collection.save_busyness_cpu(
        value,
        response_url
    )
    logger.debug("значение загрузки ЦП было сохранено")

@app.post("/query_separator")
@app.get("/query_separator")
async def query_separator(
    request: Request, 
    back_task: BackgroundTasks
):  
    '''
    Ручка, которая принимает чужие запросы, 
    которые прошли проверки в middleware check_url_in_white_list.
    После того, как запрос был перенаправлен суда, 
    то здесь вычисляется следующая сстатистика:
        время запроса,
        кол-во использовааной памяти во время запроса,
        нагруженность CPU во время запроса.

    Params:
        request: Запрос.
        back_task: Функция BackgroundTasks для создание фоновых задачей.
    '''
    id_user = str(request.state.id_user)
    main_api = request.state.main_api
    api_gateway = ManageAPIGateway(
        id_user,
        main_api
    )
    settings_url = await api_gateway.get()
    current_url_number = random.randrange(0, 2) # сделать здесь эту систему
    match current_url_number:
        case 0:
            response_url = settings_url["first_api_response"]
        case 1:
            response_url = settings_url["second_api_response"]
    cpu_before = psutil.cpu_percent(interval=1)
    tracemalloc.start()  # Включаем отслеживание памяти
    start_time = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=response_url) as response:
            response_text = await response.text()
    end_time = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    cpu_after = psutil.cpu_percent(interval=1)
    difference_cpu = cpu_after - cpu_before
    logger.debug(cpu_after)
    logger.debug(cpu_before)
    logger.debug(difference_cpu)
    back_task.add_task(
        save_time_request,
        id_user,
        main_api,
        end_time,
        response_url
    )
    back_task.add_task(
        save_memory,
        id_user,
        main_api,
        current,
        response_url
    )

    back_task.add_task(
        save_busyness_cpu,
        id_user,
        main_api,
        difference_cpu,
        response_url
    )
    return loads(response_text)
