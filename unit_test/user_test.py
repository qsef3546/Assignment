from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User,select_one
from handler.auth_handler import encoded_pw
from main import app

client = TestClient(app)
u:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="123456aB@")

'''
- 회원가입 검증
case 1: 정상적으로 회원가입
'''
def test_signup():

    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 200

'''
- 회원가입시 필요한 파라미더 값을 보내는지 검증
case 1: email 없이 보낼 때 (error code = 1101)
case 2: name 없이 보낼 때 (error code = 1102)
case 3: pw 없이 보낼 때 (error  code =1103)
'''
def test_empty_check_signup():
    cases=[
        User(name="joo",pw="123456aB@"),
        User(email="jslee@adoc.co.kr",pw="123456aB@"),
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
case 1: 소문자 포함 (error code = 1106)
case 2: 대문자 포함 (error code = 1107)
case 3: 특수 문자 포함 (error code = 1108)
'''
def test_validation_password_signup():
    testu:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="")
    pw = ["123456AB@","123456ab@","123456aBA"]
    epw = [1106,1107,1108]
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