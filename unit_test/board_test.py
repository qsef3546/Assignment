from fastapi.testclient import TestClient
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from sqlmodel import delete