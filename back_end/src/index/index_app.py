from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from fastapi import FastAPI
from fastapi.responses import JSONResponse



app = FastAPI()


@app.get("/")
async def index():
    return JSONResponse({"response": "ok"})
