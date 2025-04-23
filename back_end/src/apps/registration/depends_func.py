from fastapi import Body,HTTPException, status
from auth.utils import CryptoData
from orm.postgresql.managament.users import ManageUser


async def validate_auth_user(data = Body()):
    auth_password = CryptoData()
    user = await ManageUser.get(data["email"])
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

