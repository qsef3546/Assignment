from fastapi import APIRouter
from model.sqlconnect import user,insert,selects,update

user_router = APIRouter(prefix="/user")


@user_router.get("/list")
def user_select():
    return selects()

@user_router.post("/insert")
def user_insert(u:user):
    return insert(u)
    
@user_router.patch("/put")
def user_put(u:user):
    res = update(u)
    return {"message": "update success!"}
