from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from model.board import Board,insert,selects,select_one
from handler.auth_handler import encoded_pw
from handler.response_handler import handle_error
from datetime import datetime
board_router = APIRouter(prefix="/board")

RECENTLY = 1
VIEW = 2

def board_validation(bordname:str):
    return len(bordname) <= 100

@board_router.get("/list")
async def board_list(type: int = RECENTLY):
    boards:list = selects()
    res = []
    if not boards :
        return handle_error(1401)
    else :
        for b in boards:
            bn = {
                "board_name":b.board_name,
                "owner":b.owner,
                "view":b.view
            }
            res.append(bn)
    return JSONResponse(res,200)


@board_router.get("/{no}")
def board_one(no:int):
    b = select_one(no)
    if not b:
        return handle_error(1403)
    return JSONResponse({b},200)
    
@board_router.post("/insert")
async def board_insert(b:Board, request:Request):
    if not board_validation(b.board_name):
        return handle_error(1402)
    b.owner = request.state.u.name
    b.create_time = datetime.now()
    if insert(b) == False:
        handle_error(1200,500)
    return JSONResponse({"message" : "게시글 작성이 완료되었습니다."},200)

@board_router.put("/{board_name}")
def board_put(b:Board):
    pass
@board_router.delete("/delete")
async def board_delete():
    pass