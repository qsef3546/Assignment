from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from model.user import User,select_one
from handler.response_handler import handle_error
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
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

# JWT_PATH = ["/docs","/openapi.json","/auth/login","/user/insert","/access_token","/board/list","/board/{no}"]
JWT_PATH = ["/auth/add_access_token","/user/put","/board/insert","/board/put","/board/delete"]

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path not in JWT_PATH:
            response = await call_next(request)
            return response
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    return handle_error(1302,401)

                payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
                username = payload.get('id')
                
                u:User = None
                if not username or not (u :=select_one(email=username)):
                    return handle_error(1303,401)

                request.state.u = u
            except jwt.ExpiredSignatureError:
                return handle_error(1304,401)
            except (JWTError,ValueError):
                return handle_error(1303,401)

        else:
            return handle_error(1305,401)
        response = await call_next(request)
        return response




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
    u:User = select_one(form_data.username)
    if not u or not (encoded_pw(form_data.password) == u.pw):
        return handle_error(1110,401)
    data = {"id": form_data.username}
    access_token = create_token(data,ACCESS_TOKEN_EXPIRE_TIME)
    refresh_token = create_token(data,REFRESH_TOKEN_EXPIRE_TIME)
    return JSONResponse({"access_token":access_token,"refresh_token":refresh_token},200)

@auth_router.post("/add_access_token")
async def add_access_token(request:Request):
    data = {"id": request.state.u.email}
    access_token = create_token(data,ACCESS_TOKEN_EXPIRE_TIME)
    return JSONResponse({"access_token":access_token},200)
