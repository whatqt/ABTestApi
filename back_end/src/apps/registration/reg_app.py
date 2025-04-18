from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from auth.utils import AuthPassword
from utils.postgresql.managament.users import ManageUser
from utils.postgresql.models import Users
from auth.utils import JWToken


app = FastAPI()


@app.get("/")
async def index():
    return JSONResponse({"response": "ok"})

@app.post("/create")
async def create(data = Body()):
    auth_password = AuthPassword()
    hash_password = await auth_password.crypto_password(data["password"])
    manage_user = ManageUser(
        data["email"],
        data["username"],
        hash_password
    )
    print(hash_password)
    user = await manage_user.create()
    return JSONResponse({"response": f"{user}"})


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
            print(user)
            if user:
                return user
    raise HTTPException(423, "Неверные данные")

@app.post("/login")
async def login(user: Users = Depends(validate_auth_user)):
    jwt_token = JWToken()
    jwt_payload = {
        "sub": user.username,
        "email": user.email,
    }
    print(jwt_payload)
    token = await jwt_token.encode(
        jwt_payload
    )
    token_info = {
        "token": token,
        "type": "bearer"
    }
    print(token_info)
    return token_info
