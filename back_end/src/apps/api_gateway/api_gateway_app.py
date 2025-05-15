from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Request,
    HTTPException, status,
    Depends, 
)
from fastapi.responses import JSONResponse, RedirectResponse
from .depends_func import validate_data_from_create_test, _validate_url, get_settings_url
from auth.utils import JWToken
from jwt.exceptions import ExpiredSignatureError
from utils.logger import logger
from src.utils.alchemy_encoder import AlchemyEncoder
from src.orm.mongodb.managament.api_gateway import ManageAPIGateway
from fastapi import FastAPI, Request
import time
import random

app = FastAPI()

async def get_jwt() -> JWToken:
    return JWToken()

# @app.middleware("http")
# async def monitor_requests(request: Request, call_next):
#     start_time = time.perf_counter()
    

#     response = await call_next(request)
    
#     end_time = time.perf_counter() - start_time
#     print(end_time)


#     return response

@app.middleware("http")
async def jwt(
    request: Request, call_next: callable,
):
    authorization = request.headers.get(
        "Authorization", None
    )
    if not authorization:
        return JSONResponse(
            content="invalid token",
            status_code=status.HTTP_403_FORBIDDEN
        ) 
    try:
        token = authorization.split(" ")[1]
        payload = await JWToken().decode(token)
        request.state.payload = payload
        result = await call_next(request)
        return result
    except ExpiredSignatureError:
        logger.debug("accses токен истёк")
        return RedirectResponse("/registration/refresh")

@app.exception_handler(Exception)
async def multi_handler(request: Request, exc: Exception):
    name_handler = request.scope.get("route", None)
    if not name_handler:
        name_handler = "middleware"
    else:
        name_handler = f"func {name_handler.name}"        
    logger.error(
        f"Произошла ошибка в модуле {__name__} в {name_handler}: {exc!r}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="server error"
    )

@app.get("/records/{main_api}")
@app.get("/records")
async def get(
    request: Request,
    main_api: str = None,
):
    user_id = request.state.payload["sub"]
    api_gateway = ManageAPIGateway(
        id_user=user_id
    )
    data = await api_gateway.get(
        main_api=main_api
    )
    return JSONResponse(
        content=data,
    )
    
@app.post("/create")
async def create_test(
    request: Request,
    data = Depends(
        validate_data_from_create_test
    ),
):  
    
    payload: dict = request.state.payload
    api_gateway = ManageAPIGateway(
        id_user=payload["sub"]
    )
    result = await api_gateway.create_data(
        data=data
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"на url {data["main_api"]!r} уже есть конфигурация"
        )
    return JSONResponse(
        content={"status": "Successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@app.post("/firts_api_for_test") # чужой ответ
async def firts_api_for_test():
    return JSONResponse("Привет")

@app.post("/second_api_for_test") # чужой ответ
async def second_api_for_test():
    return JSONResponse("Пока")

@app.post("/test") # якобы чужая ручка
async def test(request: Request):
    return RedirectResponse(
        "query_separator"
    )

@app.post("/query_separator")
async def query_separator(
    request: Request, 
    validate_url = Depends(_validate_url),
    settings_url: dict = Depends(get_settings_url)
):
    current_url_number = random.randrange(0, 2)
    if current_url_number == 0:
        response_url = settings_url["first_api_response"]
        # функцияд для обработки данных
    else:
        response_url = settings_url["second_api_response"]
        # функцияд для обработки данных
    
    return RedirectResponse(response_url)

            
        
