from fastapi import Body,HTTPException, status
from auth.utils import AuthPassword
from utils.postgresql.managament.users import ManageUser



async def validate_auth_user(data = Body()):
    auth_password = AuthPassword()
    manage_user = ManageUser(
        data["email"],
        None,
        None
    )
    if (hash_password:= await manage_user.get_hash()):
        is_valid = await auth_password.validate_password(
            data["password"], hash_password
        )
        if is_valid:
            user = await manage_user.get()
            if user:
                return user
    raise HTTPException(
        status=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid data"
    )

# async def get_payload
