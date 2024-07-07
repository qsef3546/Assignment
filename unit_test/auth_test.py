from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "auth/login",
        data={"username":"z@z.com", "password":"123456aB@"}
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