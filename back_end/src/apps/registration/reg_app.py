from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Body, Depends,
    HTTPException, status,
    Response
)
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials as HTTPAuthCredentials
from fastapi.responses import JSONResponse
from auth.utils import AuthPassword
from utils.postgresql.managament.users import ManageUser
from utils.postgresql.models import Users
from auth.utils import JWToken
from .depends_func import validate_auth_user
from jwt.exceptions import InvalidTokenError



app = FastAPI()



# Зависимости
async def get_jwt() -> JWToken:
    return JWToken()

async def get_auth_pswd() -> AuthPassword:
    return AuthPassword()

@app.get("/")
async def index():
    return JSONResponse({"response": "ok"})

@app.post("/create")
async def create(
    data = Body(),
    auth_password: AuthPassword = Depends(get_auth_pswd)
):
    hash_password = await auth_password.crypto_password(data["password"])
    manage_user = ManageUser(
        data["email"],
        data["username"],
        hash_password
    )
    print(hash_password)
    user = await manage_user.create()
    return JSONResponse({"response": f"{user}"})

@app.post("/login")
async def login(
    response: Response, 
    user: Users = Depends(validate_auth_user)
):
    jwt_token = JWToken()
    jwt_payload = {
        "sub": user.email,
        "username": user.username,
        "email": user.email,
    }
    print(jwt_payload)
    access_token = await jwt_token.encode(
        jwt_payload
    )
    content = {"status": "successfully"}
    response.headers["Authorization"] = f"Bearer {access_token}"
    return JSONResponse(
        content=content,
        status_code=status.HTTP_202_ACCEPTED,
        headers=response.headers
    )

@app.post("/me")
async def about_user(
    cred: HTTPAuthCredentials = Depends(
        HTTPBearer
    ),
    jwt_token: JWToken = Depends(
        JWToken
    )
):
    token = cred.credentials
    try:
        payload = await jwt_token.decode(token)
    except InvalidTokenError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    print(payload)
    return JSONResponse(
        payload
    )