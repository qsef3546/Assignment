from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User,select_one
from model.board import Board
from sqlmodel import delete
from model.pg_sqlconf import get_session
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
- 회원가입 검증
case 1: 정상적으로 회원가입
'''
def test_signup():

    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 201

'''
- 회원가입시 필요한 파라미더 값을 보내는지 검증
case 1: email 없이 보낼 때 (error code = 1101)
case 2: name 없이 보낼 때 (error code = 1102)
case 3: pw 없이 보낼 때 (error  code =1103)
'''
def test_empty_check_signup():
    cases=[
        #case 1: email 없이 보낼 때 (error code = 1101)
        User(name="joo",pw="123456aB@"),
        #case 2: name 없이 보낼 때 (error code = 1102)
        User(email="jslee@adoc.co.kr",pw="123456aB@"),
        #case 3: pw 없이 보낼 때 (error  code =1103)
        User(email="jslee@adoc.co.kr",name="joo"),
    ]
    eca = [1101,1102,1103]
    for c, ec in zip(cases,eca):
        response = client.post('/user/insert',
                    json= c.model_dump()
                    )
        assert response.status_code == 200
        error_code = response.json().get("code")
        assert error_code == ec

'''
- 이메일 유효성 검증
case 1: 정상적인 이메일인지 확인 (error code = 1104)
'''
def test_validation_email_signup():
    testu:User = User(email="jsleeadoc.co.kr",name="joo",pw="123456aB@")
    response = client.post('/user/insert',
                json= testu.model_dump()
                )
    assert response.status_code == 200

    error_code = response.json().get("code")
    assert error_code == 1104


'''
- 비밀번호 유효성 검증 
비밀번호 = 대/소문자(각각 1글자 이상) + 특수문자 포함 8자리 이상
case 1: 8자 미만일 경우 (error code = 1105)
case 2: 소문자 포함되지 않을 경우 (error code = 1106)
case 3: 대문자 포함되지 않을 경우 (error code = 1107)
case 4: 특수 문자 포함되지 않을 경우 (error code = 1108)
'''
def test_validation_password_signup():
    testu:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="")
    pw = [
          "Ab@31",       #case 1: case 1: 8자 미만일 경우 (error code = 1105)
          "123456AB@",  #case 2: 소문자 포함되지 않을 경우 (error code = 1106)
          "123456ab@",  #case 3: 대문자 포함되지 않을 경우 (error code = 1107)
          "123456aBA"]  #case 4: 특수 문자 포함되지 않을 경우 (error code = 1108)
    epw = [1105,1106,1107,1108]
    for p, ep in zip(pw,epw):
        testu.pw = p
        response = client.post('/user/insert',
        json= testu.model_dump()
            )
        assert response.status_code == 200
        error_code = response.json().get("code")
        assert error_code == ep


'''
-특정 유저의 정보가 정상적으로 변경되는지 검증
case 1: name 및 비밀번호 변경
'''
def test_put_user():
    response = client.post('/auth/login',
                data={"username":u.email,"password":u.pw}
    )
    assert response.status_code == 200
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    assert access_token
    assert refresh_token

    fix = {
        "email": u.email,
        "name":"JJOO",
        "pw":"dDdDdD1@"
    }
    response = client.put("user/put",
               headers={"Authorization": f'Bearer {access_token}'},
               json=fix
               )
    assert response.status_code == 200
    
    usr = select_one(u.email)

    assert usr.name == fix['name']
    assert usr.pw == encoded_pw(fix['pw'])

'''
- 회원 탈퇴 검증
case 1: A 유저가 B유저를 삭제하려고할 때
case 2: 비밀번호를 다르게 입력하였을 때
case 3: 정상적으로 탈퇴가 되는지 검증
case 4: 탈퇴한 회원의 게시물의 작성자가 '탈퇴한 유저' 로 나오는지 검증
'''

def test_withdrawal():
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
        assert response.status_code == 201

        response = client.post("/auth/login",
                               data={"username":c.email,"password":c.pw}
                               )
        assert response.status_code == 200
        access_token.append(response.json().get("access_token"))
        refresh_token.append(response.json().get("refresh_token"))

    #case 1: A 유저가 B유저를 삭제하려고할 때
    response = client.request(
                            method="DELETE",
                            url='/user/delete',
                            headers={"Authorization": f'Bearer {access_token[1]}'},
                            json={"email":cases[0].email,"pw":cases[0].pw}
                            )
    assert response.status_code == 403
    error_code = response.json().get("code")
    assert error_code == 1111

    #case 2: 비밀번호를 다르게 입력하였을 때
    response = client.request(
                            method = "DELETE",
                            url='/user/delete',
                            headers={"Authorization": f'Bearer {access_token[0]}'},
                            json={"email":cases[0].email,"pw":"Abcdefg@"}
                            )
    assert response.status_code == 401
    error_code = response.json().get("code")
    assert error_code == 1109    

    #case 3: 정상적으로 탈퇴가 되는지 검증
    response = client.request(
                            method="DELETE",
                            url='/user/delete',
                            headers={"Authorization": f'Bearer {access_token[0]}'},
                            json={"email":cases[0].email,"pw":cases[0].pw}
                            )
    assert response.status_code == 200

    #case 4: 탈퇴한 회원의 게시물의 작성자가 '탈퇴한 유저' 로 나오는지 검증
    b = Board(board_name="A",content="AA")
    
    response = client.post('/board/insert',
                               headers={"Authorization": f'Bearer {access_token[1]}'},
                               json=b.model_dump()
                           )
    assert response.status_code == 201

    response = client.request(
                            method="DELETE",
                            url='/user/delete',
                            headers={"Authorization": f'Bearer {access_token[1]}'},
                            json={"email":cases[1].email,"pw":cases[1].pw}
                            )
    assert response.status_code == 200

    response = client.get('/board/list')
    assert response.status_code == 200
    board_owner = response.json()
    assert board_owner[0]['owner'] == "탈퇴한 유저"





