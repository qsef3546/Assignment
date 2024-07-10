from pymongo import MongoClient
from model.mg_sqlconf import config
from model.user import User
from pydantic import BaseModel , Field
from fastapi import Request,Response
import re
class Logs(BaseModel):
    user_id: str = Field(..., alias="userId")
    connect_ip: str = Field(..., alias="connectIP")
    request_api: str = Field(..., alias="requestApi")
    request_data: dict = Field(..., alias="requestData")
    response_status_code: int = Field(..., alias="statusCode")

client = MongoClient(str(config.SQLALCHEMY_DATABASE_URI))
db = client['api_log_db']
collection = db['logs']
collection.create_index("timestamp",expireAfterSeconds=60*60*24*60)


def mask_user_id(user_id: str):
    if len(user_id) > 4:
        return user_id[:2] + "*" * (len(user_id) - 4) + user_id[-2:]
    return "*" * len(user_id)

def mask_ip(ip: str):
    return re.sub(r'\.\d+$', '.*', ip)



async def insert_log(request:Request,response:Response):

    user_id:str = mask_user_id(request.state.u.email if request.state.u else "empty")
    connect_ip  = mask_ip(request.client.host)
    request_api = str(request.url)
    request_data = request.state.body
    response_status_code = response.status_code

    log_entry:Logs = Logs(
        userId=user_id, 
        connectIP=connect_ip,
        requestApi=request_api,
        requestData= request_data,
        statusCode= response_status_code
        )
    collection.insert_one(log_entry.model_dump(by_alias=True))