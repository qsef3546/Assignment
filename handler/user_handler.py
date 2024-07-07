from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from model.user import User,insert,select_one,update_one,withdrawal
from handler.auth_handler import encoded_pw
from handler.response_handler import handle_error
from fastapi.security import OAuth2PasswordRequestForm
import re


user_router = APIRouter(prefix="/user")

def emptycheck(u:User):
    if not u.email:
        return 1101
    if not u.name:
        return 1102
    if not u.pw:
        return 1103
    return 200

def email_validation(email:str):
    if not re.match(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',email):
        return  1104
    return 200

def password_validation(pw:str):
    if len(pw) < 8:
        return 1105
    if not re.match(r'(?=.*?[a-z])',pw):
        return 1106
    if not re.match(r'(?=.*?[A-Z])',pw):
        return 1107
    if not re.match(r'(?=.*?[#?!@$%^&*-])',pw):
        return 1108
    return 200


@user_router.post("/insert")
def user_insert(u:User):
    if (res := emptycheck(u))  != 200:
        return handle_error(res)
    elif (res := email_validation(u.email)) != 200 :
        return handle_error(res)
    elif (res := password_validation(u.pw)) != 200:
        return handle_error(res)
    
    if select_one(u.email) :
        return handle_error(1201,409)
    
    u.pw = encoded_pw(u.pw)
    if insert(u) == False:
        handle_error(1200,500)        
    else:
        return JSONResponse({"message":f"{u.email} 님의 회원가입이 완료되었습니다."},200)
    
@user_router.put("/put")
def user_put(u:User, request:Request):
    putuser = select_one(u.email)
    email = request.state.u.email
    if email != putuser.email:
        return handle_error(1111,403)
    if not putuser:
        return handle_error(1202)
            
    if u.name and putuser.name != u.name:
        putuser.name = u.name
    if u.pw:
        if (res := password_validation(u.pw)) != 200:
            return handle_error(res)
        putuser.pw = encoded_pw(u.pw)
    if (res := update_one(putuser)) == False:
        handle_error(1200,500)        
    else:
        return JSONResponse({"message":"수정이 완료되었습니다."},200)
    
@user_router.delete("/delete")
def user_delete(u:User, request:Request):
    jwt_u = request.state.u
    if not u.email or u.email != jwt_u.email:
        return handle_error(1111,403)
    
    delete_u:User = select_one(u.email)
    if not encoded_pw(u.pw) == delete_u.pw:
        return handle_error(1109,401)
    if (res := withdrawal(u.email)) == False:
        handle_error(1200,500)        
    else:
        return JSONResponse({"message":"회원 탈퇴가 완료되었습니다."},200)
