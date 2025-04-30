from fastapi import (
    Body, 
    HTTPException, 
    status
)
from utils.logger import logger


async def validate_data_from_create_test(body = Body()):
    logger.debug(body)
    required_keys = ["main_api", "first_api", "second_api"]
    if all(key in body for key in required_keys):
        logger.debug("Проверка успешно пройдена")
        return body
    logger.debug("Проверка не пройдена")
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE, 
        detail="incorrect data"
    )