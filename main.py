from fastapi import FastAPI
from handler import auth_handler,user_handler,board_handler
from sqlmodel import SQLModel
from model.pg_sqlconf import engine
app = FastAPI()
app.include_router(auth_handler.auth_router)
app.include_router(user_handler.user_router)
app.include_router(board_handler.board_router)

app.add_middleware(auth_handler.JWTAuthMiddleware)

SQLModel.metadata.create_all(engine)

