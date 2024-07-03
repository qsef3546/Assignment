from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from model.user import user,insert,select_one,update
from handler.response_handler import handle_error
from fastapi.responses import JSONResponse
from error_code import error
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import hashlib
from datetime import datetime,timedelta
auth_router = APIRouter(prefix="/auth")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_TIME = 60
REFRESH_TOKEN_EXPIRE_TIME = 60 * 24

def create_token(data:dict, expire_time:int) -> str:
    enc_data = data.copy()
    expire = datetime.now() + timedelta(minutes=expire_time)
    enc_data.update({"exp":expire})
    return jwt.encode(enc_data,SECRET_KEY,algorithm=ALGORITHM)

def encoded_pw(pw:str):
    pw_hash = hashlib.sha256()
    pw_hash.update(pw.encode())
    return pw_hash.hexdigest()

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    u:user = select_one(form_data.username)
    if not u or not (encoded_pw(form_data.password) == u.pw):
        return handle_error(1110,401)
    data = {"id": form_data.username}
    access_token = create_token(data,ACCESS_TOKEN_EXPIRE_TIME)
    refresh_token = create_token(data,REFRESH_TOKEN_EXPIRE_TIME)
    return JSONResponse({"access_token":access_token,"refresh_token":refresh_token},200)