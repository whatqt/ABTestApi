



if __name__ == "__main__":
    import uvicorn
    from src.utils.logger import logger
    logger.info("Сервер запущен")
    uvicorn.run("src.asgi:main_app", log_level="info", reload=True)
