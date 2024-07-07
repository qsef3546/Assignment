from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.user import User
from main import app

client = TestClient(app)
u:User = User(email="jslee@adoc.co.kr",name="JooSang",pw="123456aB@")

def test_signup():

    response = client.post('/user/insert',
                json= u.model_dump()
                )
    assert response.status_code == 200
