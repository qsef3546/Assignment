from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User
from model.board import Board
from sqlmodel import delete
from model.sqlconf import get_session
from main import app

client = TestClient(app)
u:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="123456aB@")

'''
initialize
'''
def test_initialize():
    with get_session() as session:
        user_statement = delete(User)
        board_statement = delete(Board)
        session.exec(user_statement)
        session.exec(board_statement)
        session.commit()

'''
board initialize

'''
def after_test_board():
    with get_session() as session:
            board_statement = delete(Board)
            session.exec(board_statement)
            session.commit()

'''
- 게시판에 글 작성 검증
case1 : 게시글 제목이 1~100자 외 입력한 경우 (error code = 1402)
case2 : 게시글 작성이 되는지 검증(이모지 포함)
'''

def test_insert_board():
    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 200

    response = client.post("/auth/login",
                            data={"username":u.email,"password":u.pw}
                          )
    assert response.status_code == 200
    access_token = response.json().get("access_token")

    #case1 : 게시글 제목이 1~100자 외 입력한 경우
    b:Board= Board(board_name="a"*101,
                   content="test 글 입니다.")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token}'},
                json= b.model_dump()
                )
    assert response.status_code == 200
    error_code = response.json().get("code")
    assert error_code == 1402

    #case2 : 게시글 작성이 되는지 검증(이모지 포함)
    b:Board= Board(board_name="이모지 test ",
                   content="😊test 글 입니다.😊")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token}'},
                json= b.model_dump()
                )
    assert response.status_code == 200

    after_test_board()
'''
- 게시글 검증
case1 : 게시글 목록이 나오는지 검증 (작성 순)
case2 : 게시글 목록이 나오는지 검증 (조회수 순)
case3 : 특정 게시글 조회가 되는지 검증
'''
def test_list_or_one_board():
    
    response = client.post("/auth/login",
                            data={"username":u.email,"password":u.pw}
                          )
    assert response.status_code == 200
    access_token = response.json().get("access_token")

    board_list = [
        Board(board_name="공지사항1",content="공지사항 1내용입니다.",view=3),  #조회수 순 확인하기 위하여 임의 조회수 값 입력
        Board(board_name="공지사항2",content="공지사항 2내용입니다.",view=5),
        Board(board_name="공지사항3",content="공지사항 3내용입니다.",view=7),
    ]
    for b in board_list:
            response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token}'},
                json= b.model_dump()
                )
            assert response.status_code == 200
#case1 : 게시글 목록이 나오는지 검증 (작성 순)
    response = client.get('/board/list')
    assert response.status_code == 200
    resb = response.json()

    for b , rb in zip(board_list,resb):
         assert b.board_name == rb['board_name']
         assert b.view == rb['view']

#case2 : 게시글 목록이 나오는지 검증 (조회수 순)
    response = client.get('/board/list',
                          params={"type":2})
    assert response.status_code == 200
    resb = response.json()

    for b , rb in zip(board_list[::-1],resb):
         assert b.board_name == rb['board_name']
         assert b.view == rb['view']

#case3 : 특정 게시글 조회가 되는지 검증
    ob = resb[0]

    response = client.get(f'/board/{ob["no"]}')
    
    assert response.status_code == 200    

    assert ob["board_name"] == response.json().get("boardname")
    assert ob["create_time"] == response.json().get("create_time")
    assert ob["view"]+1 == response.json().get("view")

    after_test_board()

'''
- 게시글 페이지네이션
@server : 5씩 pagenation 되도록 설정 되어있음
case1 : offset 0 일때 검증 (공지사항1~5 글이 조회 돼야함)
case2 : offset 1 일때 검증 (공지사항6~9 글이 조회 돼야함)
'''
def test_pagenation_board():
    pagenation = 5
    response = client.post("/auth/login",
                            data={"username":u.email,"password":u.pw}
                          )
    assert response.status_code == 200
    access_token = response.json().get("access_token")

    board_list = [
        Board(board_name="공지사항1",content="1내용입니다."),
        Board(board_name="공지사항2",content="2내용입니다."),
        Board(board_name="공지사항3",content="3내용입니다."),
        Board(board_name="공지사항4",content="4내용입니다."),
        Board(board_name="공지사항5",content="5내용입니다."),
        Board(board_name="공지사항6",content="6내용입니다."),
        Board(board_name="공지사항7",content="7내용입니다."),
        Board(board_name="공지사항8",content="8내용입니다."),
        Board(board_name="공지사항9",content="9내용입니다."),
    ]
    for b in board_list:
            response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token}'},
                json= b.model_dump()
                )
            assert response.status_code == 200

    # case1 : pageoffset 0 일때 검증 (공지사항1~5 글이 조회 돼야함)
    pageoffset = 0
    response = client.get('/board/list',
                          params={"type":1,"pageoffset":pageoffset})
    assert response.status_code == 200
    resb = response.json()

    for b , rb in zip(board_list[pagenation * 0: pagenation],resb):
         assert b.board_name == rb['board_name']

    # case2 : pageoffset 1 일때 검증 (공지사항6~9 글이 조회 돼야함)
    pageoffset = 1
    response = client.get('/board/list',
                          params={"type":1,"pageoffset":pageoffset})
    assert response.status_code == 200
    resb = response.json()

    for b , rb in zip(board_list[pagenation * pageoffset: pageoffset],resb):
         assert b.board_name == rb['board_name']

    after_test_board()
'''
- 게시글 수정 검증
case 1: 게시글 권한이 없는 유저가 타 게시글 수정 (error code = 1404)
case 2: 게시글 작성자가 쓴 게시글 수정
'''

def test_update_board():
    cases=[
        User(email="test1@adoc.co.kr",name="joo1",pw="123456aB@"),
        User(email="test2@adoc.co.kr",name="joo2",pw="123456aB@"),
    ]
    access_token=[]
    refresh_token=[]
    for c in cases:
        response = client.post('/user/insert',
                    json= c.model_dump()
                    )
        assert response.status_code == 200

        response = client.post("/auth/login",
                               data={"username":c.email,"password":c.pw}
                               )
        assert response.status_code == 200
        access_token.append(response.json().get("access_token"))
        refresh_token.append(response.json().get("refresh_token"))

    b:Board= Board(board_name="수정 전",
                   content="수정전 글 입니다.")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token[0]}'},
                json= b.model_dump()
                )
    
    assert response.status_code == 200 

    response = client.get('/board/list')
    assert response.status_code == 200

    res_no = response.json()[0]["no"]

    update_board = {
                    "no" : res_no,
                    "board_name" : "수정 후",
                    "content" : "수정후 글 입니다."
                    }
    # case 1: 게시글 권한이 없는 유저가 타 게시글 수정
    response = client.put('/board/put',
                          headers={"Authorization": f'Bearer {access_token[1]}'},
                          json = update_board
                          )
    assert response.status_code == 403
    error_code = response.json().get("code")
    assert error_code == 1404

    # case 2: 게시글 작성자가 쓴 게시글 수정
    response = client.put('/board/put',
                          headers={"Authorization": f'Bearer {access_token[0]}'},
                          json = update_board
                          )
    assert response.status_code == 200
    
    response = client.get(f'/board/{res_no}')

    assert response.status_code == 200    

    assert update_board["board_name"] == response.json().get("boardname")
    assert update_board["content"] == response.json().get("content")
    
    after_test_board()


'''
- 게시글 삭제 검증
case 1: 게시글 권한이 없는 유저가 타 게시글 삭제 (error code = 1404)
case 2: 없는 게시글 삭제 (error code = 1403)
case 3: 게시글 작성자가 쓴 게시글 수정
'''

def test_delete_board():
    cases=[
        User(email="test01@adoc.co.kr",name="joo1",pw="123456aB@"),
        User(email="test02@adoc.co.kr",name="joo2",pw="123456aB@"),
    ]
    access_token=[]
    refresh_token=[]
    for c in cases:
        response = client.post('/user/insert',
                    json= c.model_dump()
                    )
        assert response.status_code == 200

        response = client.post("/auth/login",
                               data={"username":c.email,"password":c.pw}
                               )
        assert response.status_code == 200
        access_token.append(response.json().get("access_token"))
        refresh_token.append(response.json().get("refresh_token"))

    b:Board= Board(board_name="삭제 전",
                   content="삭제전 글 입니다.")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {access_token[0]}'},
                json= b.model_dump()
                )
    
    assert response.status_code == 200 

    response = client.get('/board/list')
    assert response.status_code == 200

    res_no = response.json()[0]["no"]

    # case 1: 게시글 권한이 없는 유저가 타 게시글 삭제 (error code = 1404)
    response = client.request(
                            method="DELETE",
                            url='/board/delete',
                            headers={"Authorization": f'Bearer {access_token[1]}'},
                            params={"no":res_no}
                            )

    assert response.status_code == 403
    error_code = response.json().get("code")
    assert error_code == 1404

    # case 2: 없는 게시글 삭제 (error code = 1403)
    response = client.request(
                            method="DELETE",
                            url='/board/delete',
                            headers={"Authorization": f'Bearer {access_token[1]}'},
                            params={"no":0}
                            )

    assert response.status_code == 200
    error_code = response.json().get("code")
    assert error_code == 1403

    # case 3: 게시글 작성자가 쓴 게시글 수정
    response = client.request(
                            method="DELETE",
                            url='/board/delete',
                            headers={"Authorization": f'Bearer {access_token[0]}'},
                            params={"no":res_no}
                            )

    assert response.status_code == 200

    response = client.get(f'/board/{res_no}')

    assert response.status_code == 200    
    error_code = response.json().get("code")
    assert error_code == 1403

    after_test_board()