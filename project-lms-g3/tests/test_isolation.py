import random
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_subject_data_isolation():
    """
    Kiểm thử bảo mật Phân tách dữ liệu (Data Isolation):
    Tài khoản A tạo Môn học -> Tài khoản B đăng nhập sẽ KHÔNG thấy Môn học của A.
    """
    # 1. Đăng ký & Đăng nhập tài khoản User A
    rand_a = random.randint(10000, 99999)
    email_a = f"usera_{rand_a}@student.ptit.edu.vn"
    client.post("/auth/register", json={
        "full_name": "Nguyễn Văn A",
        "email": email_a,
        "password": "password123"
    })
    token_a = client.post("/auth/login", data={"username": email_a, "password": "password123"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Đăng ký & Đăng nhập tài khoản User B
    rand_b = random.randint(10000, 99999)
    email_b = f"userb_{rand_b}@student.ptit.edu.vn"
    client.post("/auth/register", json={
        "full_name": "Trần Văn B",
        "email": email_b,
        "password": "password123"
    })
    token_b = client.post("/auth/login", data={"username": email_b, "password": "password123"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A tạo môn học "Kiểm thử phần mềm"
    subject_code_a = f"TEST_{rand_a}"
    res_create = client.post(
        "/subjects/",
        json={
            "name": "Kiểm thử phần mềm",
            "code": subject_code_a,
            "description": "Môn học riêng của User A"
        },
        headers=headers_a
    )
    assert res_create.status_code == 201

    # 4. User A gọi API lấy danh sách môn học -> Thấy môn vừa tạo
    res_get_a = client.get("/subjects/", headers=headers_a)
    assert res_get_a.status_code == 200
    subjects_a = res_get_a.json()
    assert any(sub["code"] == subject_code_a for sub in subjects_a)

    # 5. User B gọi API lấy danh sách môn học -> KHÔNG thấy môn học của User A
    res_get_b = client.get("/subjects/", headers=headers_b)
    assert res_get_b.status_code == 200
    subjects_b = res_get_b.json()
    assert not any(sub["code"] == subject_code_a for sub in subjects_b)


def test_unauthorized_access_subjects():
    """Kiểm thử truy cập API Môn học khi KHÔNG có Token"""
    response = client.get("/subjects/")
    assert response.status_code == 401  # Bắt buộc bị chặn từ chối truy cập