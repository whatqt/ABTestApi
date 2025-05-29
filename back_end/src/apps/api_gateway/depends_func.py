from fastapi import (
    Body, 
    HTTPException, 
    status,
    Request
)
from utils.logger import logger
from json import loads
from src.orm.mongodb.managament.api_gateway import ManageAPIGateway


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

async def validate_data_from_delete(body = Body()):
    logger.debug(body)
    check = body.get("main_api", None)
    if check:
        logger.debug("Проверка успешно пройдена")
        return body
    logger.debug("Проверка не пройдена")
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE, 
        detail="incorrect data"
    )

async def validate_data_from_update(request: Request, body: dict = Body()):
    logger.debug(body)
    required_keys = [
        "main_api",
        "first_api_response",
        "first_api_percent",
        "second_api_response",
        "second_api_percent",
    ]
    check_percent = False
    if "main_api" not in body:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, 
            detail=f"a field 'main_api' with that name does not exist."
        )
            
    for key in body.keys():
        if key == "first_api_percent" or key == "second_api_percent":
            if check_percent:
                continue
            else:
                check_percent = True
                first_api_percent = body.get(
                    "first_api_percent", None
                )
                second_api_percent = body.get(
                    "second_api_percent", None
                )
                if not first_api_percent and not second_api_percent:
                    continue
                else:
                    payload = request.state.payload
                    id_user = payload["sub"]
                    api_gateway = ManageAPIGateway(
                        id_user=id_user,
                        main_api=body["main_api"]
                    )
                    if first_api_percent is None:
                        first_api_percent = await api_gateway.get()
                        first_api_percent = first_api_percent["first_api_percent"]
                    elif second_api_percent is None:
                        second_api_percent = await api_gateway.get()
                        second_api_percent = second_api_percent["second_api_percent"]
                    try:
                        if int(first_api_percent)+int(second_api_percent) == 100:
                            continue
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                                detail=f"first_api_percent and second_api_percent should both add up to 100 percent"
                            )
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"first_api_percent and second_api_percent should both add up to 100 percent"

                        )


    return body