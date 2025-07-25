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
from utils.logger import logger



app = FastAPI()



# Зависимости
async def get_crypto_data() -> CryptoData:
    return CryptoData()

# добавить суда middleware

@app.get("/")
async def index():
    return JSONResponse({"response": "ok"})

@app.post("/registration")
async def create(
    data = Body(),
    crypto_data: CryptoData = Depends(get_crypto_data)
):
    """
    Регистрация пользователя.

    Params:
        data: тело запроса
        crypto_data: класс CryptoData, который отвечает за шифрование
    """
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
    '''
    Вход пользователя в аккаунт.
    
    Params:
        user: Запись из Users
        jwt_token: Класс, для управления jwt токенами.
        refresh_token: Рефреш токен из куки. Если его нет, то будет None.
    '''
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
    # пернести создание и занесение рефреш токена
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
    '''
    Выход пользователя из системы.
    При выходе удаляются cookie.
    
    Params:
        refresh_token: Рефреш токен из куки.
        email: Почта из куки.
    '''
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
        logger.debug("Пользователь вышел")
        return response

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="access is denied"
    )
    
@app.post("/refresh")
@app.delete("/refresh")
@app.get("/refresh")
@app.patch("/refresh")
async def refresh(
    refresh_token = Cookie(default=None),
    email = Cookie(default=None),
    manage_user: ManageUser = Depends(ManageUser),
    jwt_token: JWToken = Depends(
        JWToken
    ),
):
    '''
    Обновляет accses токен, если тот истёк.
        refresh_token: Рефреш токен из куки.
        email: Почта из куки.
        manage_user: Класс для управления пользователем
        jwt_token: Класс для управления токенами
    '''
    if refresh_token and email:
        payload = await jwt_token.decode(refresh_token)
        if payload:
            user = await manage_user.get_by_email(email)
            payload = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
            }
            access_token = await jwt_token.create_accsses_token(payload)
            print(f"Bearer {access_token}") # для быстрого копирования токена в postman
            response = JSONResponse(
                content={"status": "retry"},
                status_code=status.HTTP_202_ACCEPTED,
                headers={"Authorization": f"Bearer {access_token}"}
            )   
            return response
        
    logger.debug("Неверные данные/отсутствие при запросе нового access токена")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token"
    )
