from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from model.board import Board,insert,selects,select_one,update_one,delete,RECENTLY,VIEW
from handler.response_handler import handle_error
from datetime import datetime
board_router = APIRouter(prefix="/board")

def board_validation(bordname:str):
    return (0 < len(bordname) <= 100)

@board_router.get("/list")
async def board_list(type: int = RECENTLY, pageoffset:int = 0):
    boards:list = selects(type,pageoffset)
    res = []
    if not boards :
        return handle_error(1401)
    else :
        for b in boards:
            bn = {
                "no":b.no,
                "board_name":b.board_name,
                "owner":b.owner,
                "create_time":b.create_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S.%f초"),
                "view":b.view
            }
            res.append(bn)
    return JSONResponse(res,200)


@board_router.get("/{no}")
def board_one(no:int):
    b = select_one(no)
    if not b:
        return handle_error(1403)
    res = {
        "boardname" :b.board_name,
        "owner":b.owner,
        "content":b.content,
        "view": b.view,
        "create_time":b.create_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S.%f초"),
        "fixed_time":b.fixed_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S.%f초") if b.fixed_time else ''
    }
    return JSONResponse(res,200)
    
@board_router.post("/insert")
async def board_insert(b:Board, request:Request):
    if not board_validation(b.board_name):
        return handle_error(1402)
    b.owner = request.state.u.name
    b.email = request.state.u.email
    b.create_time = datetime.now()
    if insert(b) == False:
        handle_error(1200,500)
    return JSONResponse({"message" : "게시글 작성이 완료되었습니다."},200)

@board_router.put("/put")
def board_put(b:Board, request:Request):
    if not b.no:
        return handle_error(1403)
    
    fixb = select_one(b.no)
    if not fixb:
        return handle_error(1403)
    
    email = request.state.u.email

    if email != fixb.email:
        return handle_error(1404,403)
    
    if b.board_name:
        if not board_validation(b.board_name):
            return handle_error(1402)
        fixb.board_name = b.board_name

    if b.content:
        fixb.content = b.content

    fixb.fixed_time = datetime.now()

    if update_one(fixb) == False:
        handle_error(1200,500)
    return JSONResponse({"message" : "게시글 수정이 완료되었습니다"},200)

@board_router.delete("/delete")
async def board_delete(no:int,request:Request):
    if not no:
        return handle_error(1403)
    
    fixb = select_one(no)
    if not fixb:
        return handle_error(1403)
    
    email = request.state.u.email

    if email != fixb.email:
        return handle_error(1404,403)
    
    if delete(fixb.no) == False:
        handle_error(1200,500)
    return JSONResponse({"message" : "게시글 삭제가 되었습니다."})