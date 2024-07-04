from fastapi import FastAPI
from handler import auth_handler,user_handler
app = FastAPI()
app.include_router(auth_handler.auth_router)
app.include_router(user_handler.user_router)

app.add_middleware(auth_handler.JWTAuthMiddleware)

@app.get("/login")
def hello():
    return {"message": "hello world"}


@app.get("/")
def root():
    return {"message": "root tesst"}

