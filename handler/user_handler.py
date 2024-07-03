from fastapi import APIRouter
from fastapi.responses import JSONResponse
from model.user import user,insert,selects,select_one,update
from handler.auth_handler import encoded_pw
from handler.response_handler import handle_error
import re


user_router = APIRouter(prefix="/user")

def emptycheck(u:user):
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


@user_router.get("/list")
def user_select():
    return selects()

@user_router.post("/insert")
def user_insert(u:user):
    if (res := emptycheck(u))  != 200:
        return handle_error(res)
    elif (res := email_validation(u.email)) != 200 :
        return handle_error(res)
    elif (res := password_validation(u.pw)) != 200:
        return handle_error(res)
    
    if select_one(u.email) :
        return handle_error(1201,409)
    
    u.pw = encoded_pw(u.pw)
    if (res := insert(u)) == False:
        handle_error(1200,500)        
    else:
        return JSONResponse({"message":f"{u.email} 님의 회원가입이 완료되었습니다."},200)
    
@user_router.patch("/put")
def user_put(u:user):
    putuser = select_one(u.email)
    if not putuser:
        return handle_error(1202)
            
    if u.name and putuser.name != u.name:
        putuser.name = u.name
    if u.pw:
        if (res := password_validation(u.pw)) != 200:
            return handle_error(res)
        putuser.pw = encoded_pw(u.pw)
    if (res := update(putuser)) == False:
        handle_error(1200,500)        
    else:
        return JSONResponse({"message":"수정이 완료되었습니다."},200)
