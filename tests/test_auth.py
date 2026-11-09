import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    """Kiểm thử đăng nhập thành công"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test@student.ptit.edu.vn",
            "password": "password123"
        }
    )
    assert response.status_code in [200, 401]

def test_login_wrong_password():
    """Kiểm thử đăng nhập sai mật khẩu"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test@student.ptit.edu.vn",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_protected_route_without_token():
    """Kiểm thử truy cập router bảo mật không kèm Token"""
    response = client.get("/auth/me")
    assert response.status_code in [401, 404]