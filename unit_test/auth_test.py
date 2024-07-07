from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User
from model.board import Board
from sqlmodel import delete
from model.sqlconf import get_session
from main import app

client = TestClient(app)

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


def test_login():
    u:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="123456aB@")
    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 200

    response = client.post(
        "auth/login",
        data={"username":u.email, "password":u.pw}
        )
    
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    assert access_token
    assert refresh_token


def test_invalid_login():
    response = client.post(
        "auth/login",
        data={"username":"test@test.com", "password":"123123"}
        )
    
    assert response.status_code == 401
    error_code = response.json().get("code")
    assert error_code == 1110