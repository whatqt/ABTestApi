from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Request,
    HTTPException, status,
    Body, Depends, 
)
from fastapi.security import HTTPAuthorizationCredentials as HTTPAuthCredentials
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from .depends_func import validate_data_from_create_test
from auth.utils import JWToken
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError


app = FastAPI()

@app.middleware("http")
async def jwt(
    request: Request, call_next: callable
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
        await JWToken().decode(token)
        result = await call_next(request)
        return result
    except InvalidTokenError as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="invalid token"
        )    



@app.post("/")
async def create_test(
    data = Depends(
        validate_data_from_create_test
    )   
):
    return JSONResponse("test")