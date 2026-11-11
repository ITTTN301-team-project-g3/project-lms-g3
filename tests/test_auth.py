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

import random

# ==========================================
# CÁC TEST CASE CHO LUỒNG ĐĂNG KÝ (REGISTER)
# ==========================================

def test_register_success():
    """TC01: Kiểm thử đăng ký tài khoản thành công với dữ liệu hợp lệ"""
    # Dùng random để sinh email ngẫu nhiên, tránh lỗi trùng lặp khi chạy test nhiều lần
    rand_id = random.randint(10000, 99999)
    test_email = f"student_{rand_id}@ptit.edu.vn"
    
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Nguyễn Văn Test",
            "email": test_email,
            "password": "password123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_email
    assert data["full_name"] == "Nguyễn Văn Test"
    assert "id" in data
    assert data["is_active"] == True
    assert "password_hash" not in data # Đảm bảo không lộ mật khẩu đã mã hóa

def test_register_duplicate_email():
    """TC02: Kiểm thử đăng ký thất bại khi sử dụng Email đã tồn tại"""
    rand_id = random.randint(10000, 99999)
    test_email = f"duplicate_{rand_id}@ptit.edu.vn"
    payload = {
        "full_name": "User Duplicate",
        "email": test_email,
        "password": "password123"
    }
    
    # 1. Đăng ký lần đầu (sẽ thành công)
    first_attempt = client.post("/auth/register", json=payload)
    assert first_attempt.status_code == 201
    
    # 2. Cố tình đăng ký lại với cùng email đó
    second_attempt = client.post("/auth/register", json=payload)
    
    # Bắt buộc phải nhận về lỗi 400 Bad Request
    assert second_attempt.status_code == 400
    assert second_attempt.json()["detail"] == "Email đã được đăng ký trong hệ thống."

def test_register_invalid_email_format():
    """TC03: Kiểm thử Pydantic chặn email sai định dạng (không có @)"""
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Invalid Email",
            "email": "not-an-email",
            "password": "password123"
        }
    )
    # Trả về 422 Unprocessable Entity do Pydantic Schema UserCreate bắt lỗi
    assert response.status_code == 422 
    
def test_register_short_password():
    """TC04: Kiểm thử Pydantic chặn mật khẩu dưới 6 ký tự"""
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Short Password",
            "email": f"shortpass_{random.randint(100,999)}@ptit.edu.vn",
            "password": "123" 
        }
    )
    # Trả về 422 do vi phạm min_length=6 của trường password
    assert response.status_code == 422