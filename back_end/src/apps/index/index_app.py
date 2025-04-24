from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.logger import logger


app = FastAPI()

@app.get("/")
async def index():
    logger.debug(f"получен запрос в {index.__name__}")
    return JSONResponse({"response": "ok"})
