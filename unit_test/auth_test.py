from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User
from model.board import Board
from sqlmodel import delete
from model.pg_sqlconf import get_session
from main import app

client = TestClient(app)
expired_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Inp6QHp6LmNvbSIsImV4cCI6MTcyMDMyNjE2Mn0.lk5hqAYYJXvLwmTLSaEQlOT7niEP37rlWSTLBB0WS1M'

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
- 로그인 검증
'''
def test_login():
    u:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="123456aB@")
    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 201

    response = client.post(
        "auth/login",
        data={"username":u.email, "password":u.pw}
        )
    
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    assert access_token
    assert refresh_token


'''
- 없는 유저의 로그인 검증
'''
def test_invalid_login():
    response = client.post(
        "auth/login",
        data={"username":"test@test.com", "password":"123123"}
        )
    
    assert response.status_code == 401
    error_code = response.json().get("code")
    assert error_code == 1110


'''
- 토근 만료 검증 (error code: 1304)
'''
def test_expired_token():
    b:Board= Board(board_name="토큰 만료 테스트 ",
                   content="토큰 만료 테스트 글입니다.")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer {expired_access_token}'},
                json= b.model_dump()
                )
    
    assert response.status_code == 401
    error_code = response.json().get("code")
    assert error_code == 1304

'''
- 유효하지 않은 token 검증 (error code: 1303)
'''
def test_valid_token():
    b:Board= Board(board_name="유효하지 않은 token  테스트 ",
                   content="유효하지 않은 token 입니다.")
    response = client.post('/board/insert',
                headers={"Authorization": f'Bearer asdfkiaweifj123'},
                json= b.model_dump()
                )
    
    assert response.status_code == 401
    error_code = response.json().get("code")
    assert error_code == 1303