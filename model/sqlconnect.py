from sqlmodel import Field, SQLModel, create_engine, Session, select
from model.sqlconf import config
from error_code import error
from fastapi.responses import JSONResponse
import hashlib
import re
engine = create_engine(str(config.SQLALCHEMY_DATABASE_URI))
SQLModel.metadata.create_all(engine)
pw_hash = hashlib.sha256()

class user(SQLModel, table=True):
    email: str = Field(unique=True,nullable=False,primary_key=True)
    name: str = Field(nullable=False)
    pw: str = Field(nullable=False)

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

    
def selects():
    with Session(engine) as session:
        statement = select(user)
        res = session.exec(statement).all()
        s = {'res':[x.__dict__ for x in res]}
        return s
def select_one(email:str):
    with Session(engine) as session:
        statement = select(user).where(user.email==email)
        userinfo = session.exec(statement).one_or_none()
        if not userinfo:
            return None
        else:
            return userinfo
def insert(u:user):
    res = emptycheck(u) 
    if res != 200:
        return JSONResponse({"code":res,"message":error.errorcode[res]},200)
    
    res = email_validation(u.email)
    if res != 200 :
        return JSONResponse({"code":res,"message":error.errorcode[res]},200)
    
    res = password_validation(u.pw)
    if res != 200:
        return JSONResponse({"code":res,"message":error.errorcode[res]},200)
    
    try:
        res = select_one(u.email)
        if res :
            return JSONResponse({"code":1109,"message":error.errorcode[1109].format(u.email)},200)
            
        pw_hash.update(u.pw.encode())
        u.pw = pw_hash.hexdigest()
        with Session(engine) as session:
            try:
                session.add(u)
                session.commit()
                session.refresh(u)
            except Exception as e:
                session.rollback()
                raise e
    except Exception as e:
        return JSONResponse({"code":1200,"message":error.errorcode[1200],"error message":f'{e}'},500)
    
    return JSONResponse({"message":f"{u.email} 님의 회원가입이 완료되었습니다."},200)



def update(u:user):
    with Session(engine) as session:
        statement = select(user).where(user.id == u.id)
        putuser = session.exec(statement).one()
        if not putuser:
            return {"message":"id is not exist"}
        if u.pw is not None:
            putuser.pw = u.pw
        if putuser.name != u.name:
            putuser.name = u.name
        if (putuser.age != u.age) and u.age != None:
            putuser.age = u.age
        session.add(putuser)
        session.commit()

