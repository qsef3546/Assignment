from fastapi.testclient import TestClient
import sys,os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User,select_one
from model.board import Board,insert
from sqlmodel import delete
from model.sqlconf import get_session
from handler.auth_handler import encoded_pw
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
- 게시판에 글 작성 검증
case1 : 게시글 제목이 1~100자 외 입력한 경우
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
    b:Board= Board(board_name="aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffggggggggghhhhhhhhhhiiiiiiiiiijjjjjjjjjjjj",
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

    with get_session() as session:
        board_statement = delete(Board)
        session.exec(board_statement)
        session.commit()
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
    print(ob)
    response = client.get(f'/board/{ob["no"]}')
    
    assert response.status_code == 200    

    assert ob["board_name"] == response.json().get("boardname")
    assert ob["create_time"] == response.json().get("create_time")
    assert ob["view"]+1 == response.json().get("view")

    with get_session() as session:
        board_statement = delete(Board)
        session.exec(board_statement)
        session.commit()