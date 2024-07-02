from fastapi import APIRouter
from model.sqlconnect import user,insert,selects,update

auth_router = APIRouter(prefix="/auth")
@auth_router.get("/login")
def hello():
    return {"message": "hello world"}