from fastapi import Body,HTTPException, status
from auth.utils import CryptoData
from orm.postgresql.managament.users import ManageUser
from orm.postgresql.models import Users
from typing import Union

async def validate_auth_user(data = Body()) -> Union[Users, HTTPException]:
    '''
    Проверяет, есть ли пользователь в БД? путём провеки кэша 
    пароля и самого пароля. Если проверка пройдена успешно, то
    отдаёт пользователя, иначе возвращает ошибку.

    Params:
        data: Тело запроса.
    :return Users | HTTPException: возвращает пользователя или ошибку
    '''
    if ("email" not in data) or ("password" not in data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Укажите email и password"
        )

    auth_password = CryptoData()
    user = await ManageUser.get_by_email(data["email"])
    if user:
        if (hash_password:= user.password):
            is_valid = await auth_password.validate_data(
                data["password"], hash_password
            )
            if is_valid:
                return user
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid data"
    )

