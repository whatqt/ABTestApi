from fastapi import (
    Body, 
    HTTPException, 
    status,
    Request
)
from utils.logger import logger
from json import loads
from src.orm.mongodb.managament.api_gateway import ManageAPIGateway
from typing import Union



async def validate_data_from_create(
    body = Body()
) -> Union[dict, HTTPException]:
    '''
    Валидация body запроса для создания данных.
    В body обязаны быть все значения, которые упоминаются в 
    списке required_keys. Если body прошло валидацию, то
    результатом будет body, иначе будет ошибка.
    
    Params:
        body: Тело запроса.

    :return dict | HTTPException: Body или ошибка
    '''
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

async def validate_data_from_delete(
    body = Body()
) -> Union[dict, HTTPException]:
    '''
    Валидация body запроса для удаление данных.
    В body должно быть main_api, иначе вернётся ошибка.
    
    Params:
        body: Тело запроса.

    :return dict | HTTPException: Body или ошибка
    '''
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

async def validate_data_from_update(
    request: Request, 
    body: dict = Body()
) -> Union[dict, HTTPException]:
    '''
    Валидация body запроса для обновления данных.
    В body обязаны быть main_api, если его не будет, то будет исключение.
    Так же проверяется наличие записи в MongoDB и
    если записи нет, то вызывается исключение.
    Опционально могут быть ключи из списка required_keys для обновления данных.
    Если будут произвольные ключи, то будет вызвано исключение.

    Так же детальная валидация двух полей: first_api_percent и second_api_percent.
    Если они указаны оба, то тогда проверяется их результат 
    и если результат != 100, то вызывается исключение.
    Если указано только одно поле, то второе значение будет взято из MongoDB 
    и только потом будет проверка сложением.
    
    Params:
        request: Запрос.
        body: Тело запроса.

    :return dict | HTTPException: Body или ошибка
    '''
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
    payload = request.state.payload
    id_user = payload["sub"]
    api_gateway = ManageAPIGateway(
        id_user=id_user,
        main_api=body["main_api"]
    )       
    check = await api_gateway.get()
    if not check:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, 
            detail=f"Такого {body["main_api"]} url не существует."
        )
    for key in body.keys():
        if check_percent:
            if key not in required_keys:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                    detail=f"Такой параметр как {key!r} не существует"
                )  

        if key == "first_api_percent" or key == "second_api_percent":
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