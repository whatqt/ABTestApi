from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import (
    FastAPI, Body, Depends,
    HTTPException, status,
    Request, Cookie,
)
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials as HTTPAuthCredentials
from fastapi.responses import JSONResponse, RedirectResponse
from auth.utils import CryptoData
from orm.postgresql.managament.users import ManageUser
from orm.postgresql.models import Users
from auth.utils import JWToken
from .depends_func import validate_auth_user
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError



app = FastAPI()



# Зависимости
async def get_jwt() -> JWToken:
    return JWToken()

async def get_crypto_data() -> CryptoData:
    return CryptoData()

@app.get("/")
async def index():
    return JSONResponse({"response": "ok"})

@app.post("/create")
async def create(
    data = Body(),
    crypto_data: CryptoData = Depends(get_crypto_data)
):
    hash_password = await crypto_data.crypto_data(data["password"])
    user = await ManageUser.create(
        data["email"],
        data["username"],
        hash_password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Такой пользователь уже существует"
        )
    return JSONResponse({"response": f"Пользователь успешно создан"})

@app.post("/login")
async def login(
    user: Users = Depends(validate_auth_user),
    jwt_token: JWToken = Depends(JWToken),
    refresh_token = Cookie(default=None),
):  
    if refresh_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access is denied"
        )
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
    }
    access_token = await jwt_token.create_accsses_token(
        payload
    )
    refresh_token = await jwt_token.create_refresh_token(
        {"sub": str(user.id)}
    )
    await ManageUser.save_refresh_token(user, refresh_token)
    response = JSONResponse(
        content={"status": "successfully"},
        status_code=status.HTTP_202_ACCEPTED,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token,
        httponly=True
    )
    response.set_cookie(
        key="email",
        value=user.email,
        httponly=True
    )
    return response

@app.post("/logout")
async def logout(
    refresh_token = Cookie(default=None),
    email = Cookie(default=None),
):
    if refresh_token or email:
        response = JSONResponse(
            content={"message": "successfully"},
            status_code=status.HTTP_202_ACCEPTED,
        )
        response.delete_cookie(
            key="refresh_token",
            httponly=True
        )
        response.delete_cookie(
            key="email",
            httponly=True
        )
        return response
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="access is denied"
    )
    

@app.get("/refresh")
@app.post("/refresh")
async def refresh(
    request: Request,
    refresh_token = Cookie(default=None),
    email = Cookie(default=None),
    manage_user: ManageUser = Depends(ManageUser),
    jwt_token: JWToken = Depends(
        JWToken
    ),
):
    if refresh_token and email:
        payload = await jwt_token.decode(refresh_token)
        if payload:
            user = await manage_user.get(email)
            payload = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
            }
            access_token = await jwt_token.create_accsses_token(payload)
            print(f"Bearer {access_token}")
            response = JSONResponse(
                content={"status": "retry"},
                status_code=status.HTTP_202_ACCEPTED,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token"
    )

@app.post("/me")
async def about_user(
    request: Request,
    cred: HTTPAuthCredentials = Depends(
        HTTPBearer()
    ),
    jwt_token: JWToken = Depends(
        JWToken
    ),    
):  
    token = cred.credentials
    try:
        payload = await jwt_token.decode(token)
    except ExpiredSignatureError as e:
        return RedirectResponse("/registration/refresh")
    except InvalidTokenError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    return JSONResponse(
        payload
    )