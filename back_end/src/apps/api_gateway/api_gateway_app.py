from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Request,
    HTTPException, status,
    Depends, 
)
from fastapi.responses import JSONResponse, RedirectResponse
from .depends_func import (
    validate_data_from_create, 
    validate_data_from_delete,
    validate_data_from_update
)
from auth.utils import JWToken
from jwt.exceptions import ExpiredSignatureError
from utils.logger import logger
from src.orm.mongodb.managament.api_gateway import ManageAPIGateway
from src.orm.postgresql.managament.white_list_urls import ManageWhiteListUrls
from src.orm.postgresql.managament.users import ManageUser
from src.orm.mongodb.managament.api_gateway import ManageAPIGateway




app = FastAPI()

@app.middleware("http")
async def jwt(
    request: Request, call_next: callable,
):
    authorization = request.headers.get(
        "Authorization", None
    )
    if not authorization:
        logger.debug("invalid token")
        return JSONResponse(
            content="invalid token",
            status_code=status.HTTP_403_FORBIDDEN
        ) 
    jwt_token = JWToken()
    try:
        token = authorization.split(" ")[1]
        payload = await jwt_token.decode(token)
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
        f"Произошла ошибка в модуле {__name__} в {name_handler}: {exc}"
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
        id_user=user_id,
        main_api=main_api
    )
    if main_api:
        data = await api_gateway.get()
    else:
        data = await api_gateway.get_all_main_api()
    content = {
        "data": data
    }
    return JSONResponse(
        content=content,
    )

@app.post("/create")
async def create(
    request: Request,
    data = Depends(
        validate_data_from_create,

    ),
):  
    payload: dict = request.state.payload
    id_user = payload["sub"]
    user = await ManageUser.get_by_id(int(id_user))
    api_gateway = ManageAPIGateway(
        id_user=id_user,
        main_api=data["main_api"]
    )
    result_mongodb = await api_gateway.create_data(
        data=data
    )
    result_postgres = await ManageWhiteListUrls.create(
        url=data["main_api"],
        user=user
    )
    if not result_mongodb or not result_postgres:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"на url {data["main_api"]!r} уже есть конфигурация"
        )
    return JSONResponse(
        content={"status": "Successfully created"},
        status_code=status.HTTP_201_CREATED
    )

@app.delete("/delete")
async def delete(
    request: Request,
    data = Depends(validate_data_from_delete)
):  
    main_api = data["main_api"]
    id_user = request.state.payload["sub"]
    api_gateway = ManageAPIGateway(
        id_user=id_user,
        main_api=main_api
    )
    result_mongodb = await api_gateway.delete()
    result_postgres = await ManageWhiteListUrls.delete(main_api)
    if result_mongodb and result_postgres:
        return JSONResponse(
            content={"status": "Successfully deleted"},
            status_code=status.HTTP_202_ACCEPTED
        )
    return JSONResponse(
        content={
            "status": f"Not deleted. Reason: the object {main_api!r} was not found"
        },
        status_code=status.HTTP_202_ACCEPTED
    )

@app.patch("/update")
async def update(
    request: Request,
    data = Depends(validate_data_from_update)
):
    main_api = data["main_api"]
    id_user = request.state.payload["sub"]
    api_gateway = ManageAPIGateway(
        id_user=id_user,
        main_api=main_api
    )
    result = await api_gateway.update(data)
    if not result:
        return JSONResponse(
            content={"status": f"такого main_api {main_api} не существует"},
            status_code=status.HTTP_202_ACCEPTED
        )
    logger.debug(result)
    return JSONResponse(
        content={"status": "Successfully updated"},
        status_code=status.HTTP_202_ACCEPTED
    )
    
    
            
        
