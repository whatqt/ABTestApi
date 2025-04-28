from utils.logger import logger
from functools import wraps
from fastapi import HTTPException
from fastapi import FastAPI, Request, HTTPException, status, Response


def try_except(func):
    async def wrapper():
        try:
            result = await func()
            print("test")
            return result
        except Exception as e:
            logger.error(f"произошла ошибка в функции {func.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="server error"
            )
    return wrapper

    

