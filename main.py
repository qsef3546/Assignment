from fastapi import FastAPI
from model.sqlconnect import user,insert,selects,update
app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "hello world"}


@app.get("/")
def root():
    return {"message": "root tesst"}

@app.post("/user/insert")
def user_insert(u:user):
    return insert(u)
    

@app.get("/user/list")
def user_select():
    return selects()

@app.patch("/user/put")
def user_put(u:user):
    res = update(u)
    return {"message": "update success!"}


