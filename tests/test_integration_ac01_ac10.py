import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    # Chỉ override DB sang SQLite in-memory; giữ nguyên luồng xác thực JWT thật của hệ thống
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def register_and_login(client: TestClient, full_name: str, email: str, password: str) -> dict:
    """Hàm hỗ trợ đăng ký tài khoản, đăng nhập lấy JWT Token và trả về Authorization header."""
    reg_res = client.post(
        "/auth/register",
        json={"full_name": full_name, "email": email, "password": password},
    )
    assert reg_res.status_code in (200, 201), f"Đăng ký thất bại: {reg_res.text}"

    login_res = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_res.status_code == 200, f"Đăng nhập thất bại: {login_res.text}"
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# =====================================================================
# AC-01: ĐĂNG KÝ TÀI KHOẢN MỚI
# =====================================================================
def test_ac01_user_registration(client: TestClient):
    # 1. Đăng ký hợp lệ
    res = client.post(
        "/auth/register",
        json={
            "full_name": "Nguyễn Gia Hân",
            "email": "giahan.ac01@studenthub.edu.vn",
            "password": "Password@123",
        },
    )
    assert res.status_code in (200, 201)
    data = res.json()
    assert data["email"] == "giahan.ac01@studenthub.edu.vn"
    assert "password" not in data
    assert "password_hash" not in data

    # 2. Chặn đăng ký trùng email
    dup_res = client.post(
        "/auth/register",
        json={
            "full_name": "Tài khoản trùng",
            "email": "giahan.ac01@studenthub.edu.vn",
            "password": "Password@123",
        },
    )
    assert dup_res.status_code in (400, 409)

    # 3. Validate email sai định dạng
    invalid_res = client.post(
        "/auth/register",
        json={
            "full_name": "Email sai",
            "email": "khong-phai-email",
            "password": "123",
        },
    )
    assert invalid_res.status_code == 422


# =====================================================================
# AC-02: ĐĂNG NHẬP & XÁC THỰC JWT TOKEN
# =====================================================================
def test_ac02_login_and_jwt_authentication(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "full_name": "Sinh Viên AC02",
            "email": "sv.ac02@studenthub.edu.vn",
            "password": "SecretPassword@123",
        },
    )

    # 1. Đăng nhập sai mật khẩu -> bị từ chối
    wrong_res = client.post(
        "/auth/login",
        data={"username": "sv.ac02@studenthub.edu.vn", "password": "SaiMatKhau"},
    )
    assert wrong_res.status_code in (400, 401)

    # 2. Đăng nhập đúng -> nhận Bearer Token
    ok_res = client.post(
        "/auth/login",
        data={"username": "sv.ac02@studenthub.edu.vn", "password": "SecretPassword@123"},
    )
    assert ok_res.status_code == 200
    token = ok_res.json().get("access_token")
    assert token

    # 3. Chặn truy cập API bảo vệ khi thiếu token hoặc token sai
    assert client.get("/subjects/").status_code == 401
    assert client.get("/tasks/", headers={"Authorization": "Bearer token_gia_mao"}).status_code == 401


# =====================================================================
# AC-03 & AC-04: QUẢN LÝ MÔN HỌC (TẠO, XEM, SỬA, XÓA & RÀNG BUỘC)
# =====================================================================
def test_ac03_ac04_subject_crud_and_constraints(client: TestClient):
    headers = register_and_login(client, "SV Môn Học", "sub@studenthub.edu.vn", "Pass@12345")

    # AC-03: Tạo môn học mới và xem danh sách
    create_res = client.post(
        "/subjects/",
        json={"code": "INT3306", "name": "Phát triển ứng dụng Web"},
        headers=headers,
    )
    assert create_res.status_code in (200, 201)
    subject_id = create_res.json()["id"]

    list_res = client.get("/subjects/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["code"] == "INT3306"

    # AC-04: Cập nhật tên môn học
    update_res = client.put(
        f"/subjects/{subject_id}",
        json={"code": "INT3306", "name": "Phát triển ứng dụng Web nâng cao"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Phát triển ứng dụng Web nâng cao"

    # Xóa môn học rỗng -> thành công
    del_res = client.delete(f"/subjects/{subject_id}", headers=headers)
    assert del_res.status_code in (200, 204)
    assert client.get("/subjects/", headers=headers).json() == []


# =====================================================================
# AC-05, AC-06 & AC-07: QUẢN LÝ BÀI TẬP (CRUD & ĐỔI TRẠNG THÁI NHANH)
# =====================================================================
def test_ac05_ac06_ac07_task_crud_and_status_transition(client: TestClient):
    headers = register_and_login(client, "SV Bài Tập", "task@studenthub.edu.vn", "Pass@12345")

    sub_res = client.post(
        "/subjects/",
        json={"code": "SE104", "name": "Công nghệ phần mềm"},
        headers=headers,
    )
    subject_id = sub_res.json()["id"]

    # AC-05: Tạo bài tập mới
    due = (datetime.now() + timedelta(days=5)).isoformat()
    create_res = client.post(
        "/tasks/",
        json={
            "title": "Nộp báo cáo SRS",
            "description": "Chuẩn IEEE 830",
            "due_date": due,
            "status": "TODO",
            "subject_id": subject_id,
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]

    # Chặn tạo bài tập vào môn học không tồn tại
    bad_task = client.post(
        "/tasks/",
        json={"title": "Bài tập lỗi", "subject_id": 99999},
        headers=headers,
    )
    assert bad_task.status_code == 404

    # AC-06: Sửa thông tin bài tập
    put_res = client.put(
        f"/tasks/{task_id}",
        json={"title": "Nộp báo cáo SRS (Bản cuối)", "description": "Đã rà soát"},
        headers=headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Nộp báo cáo SRS (Bản cuối)"

    # AC-07: Đổi nhanh trạng thái TODO -> IN_PROGRESS -> DONE
    p1 = client.patch(f"/tasks/{task_id}/status", json={"status": "IN_PROGRESS"}, headers=headers)
    assert p1.status_code == 200
    assert p1.json()["status"] == "IN_PROGRESS"

    p2 = client.patch(f"/tasks/{task_id}/status", json={"status": "DONE"}, headers=headers)
    assert p2.status_code == 200
    assert p2.json()["status"] == "DONE"

    # AC-06: Xóa bài tập
    del_res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 204
    assert client.get("/tasks/", headers=headers).json() == []


# =====================================================================
# AC-08: TÌM KIẾM & LỌC BÀI TẬP ĐA ĐIỀU KIỆN
# =====================================================================
def test_ac08_search_and_filter_tasks(client: TestClient):
    headers = register_and_login(client, "SV Bộ Lọc", "filter@studenthub.edu.vn", "Pass@12345")

    sub1 = client.post("/subjects/", json={"code": "CSDL", "name": "Cơ sở dữ liệu"}, headers=headers).json()
    sub2 = client.post("/subjects/", json={"code": "MMT", "name": "Mạng máy tính"}, headers=headers).json()

    client.post("/tasks/", json={"title": "Thiết kế ERD", "status": "DONE", "subject_id": sub1["id"]}, headers=headers)
    client.post("/tasks/", json={"title": "Viết câu lệnh SQL", "status": "TODO", "subject_id": sub1["id"]}, headers=headers)
    client.post("/tasks/", json={"title": "Cấu hình Router Cisco", "status": "IN_PROGRESS", "subject_id": sub2["id"]}, headers=headers)

    # 1. Tìm kiếm theo từ khóa không phân biệt hoa/thường
    res_search = client.get("/tasks/?search=sql", headers=headers)
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["title"] == "Viết câu lệnh SQL"

    # 2. Lọc theo môn học
    res_sub = client.get(f"/tasks/?subject_id={sub1['id']}", headers=headers)
    assert len(res_sub.json()) == 2

    # 3. Kết hợp môn học + trạng thái
    res_combo = client.get(f"/tasks/?subject_id={sub1['id']}&status=DONE", headers=headers)
    assert len(res_combo.json()) == 1
    assert res_combo.json()[0]["title"] == "Thiết kế ERD"


# =====================================================================
# AC-09: THỐNG KÊ TỔNG QUAN DASHBOARD (TÀI KHOẢN MỚI & CÓ DỮ LIỆU)
# =====================================================================
def test_ac09_dashboard_statistics(client: TestClient):
    headers = register_and_login(client, "SV Dashboard", "dash@studenthub.edu.vn", "Pass@12345")

    # 1. Tài khoản mới chưa có dữ liệu -> mọi chỉ số đều bằng 0
    empty_stats = client.get("/dashboard/stats", headers=headers).json()
    assert empty_stats == {
        "total_subjects": 0,
        "total_tasks": 0,
        "todo_tasks": 0,
        "in_progress_tasks": 0,
        "done_tasks": 0,
        "completion_rate": 0.0,
    }

    # 2. Tạo 2 môn học và 4 bài tập (1 TODO, 1 IN_PROGRESS, 2 DONE -> 50.0%)
    s1 = client.post("/subjects/", json={"code": "SUB1", "name": "Môn 1"}, headers=headers).json()
    s2 = client.post("/subjects/", json={"code": "SUB2", "name": "Môn 2"}, headers=headers).json()

    client.post("/tasks/", json={"title": "T1", "status": "TODO", "subject_id": s1["id"]}, headers=headers)
    client.post("/tasks/", json={"title": "T2", "status": "IN_PROGRESS", "subject_id": s1["id"]}, headers=headers)
    client.post("/tasks/", json={"title": "T3", "status": "DONE", "subject_id": s2["id"]}, headers=headers)
    client.post("/tasks/", json={"title": "T4", "status": "DONE", "subject_id": s2["id"]}, headers=headers)

    stats = client.get("/dashboard/stats", headers=headers).json()
    assert stats["total_subjects"] == 2
    assert stats["total_tasks"] == 4
    assert stats["todo_tasks"] == 1
    assert stats["in_progress_tasks"] == 1
    assert stats["done_tasks"] == 2
    assert stats["completion_rate"] == 50.0


# =====================================================================
# AC-10: CẢNH BÁO HẠN NỘP & BẢO MẬT PHÂN TÁCH DỮ LIỆU (DATA ISOLATION)
# =====================================================================
def test_ac10_deadline_warnings_and_data_isolation(client: TestClient):
    headers_a = register_and_login(client, "Sinh Viên A", "user_a@studenthub.edu.vn", "Pass@12345")
    headers_b = register_and_login(client, "Sinh Viên B", "user_b@studenthub.edu.vn", "Pass@12345")

    sub_a = client.post("/subjects/", json={"code": "IT001", "name": "Nhập môn lập trình"}, headers=headers_a).json()

    # Tạo 1 bài quá hạn và 1 bài sắp đến hạn của User A
    overdue_task = client.post(
        "/tasks/",
        json={
            "title": "Bài quá hạn của A",
            "due_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "status": "TODO",
            "subject_id": sub_a["id"],
        },
        headers=headers_a,
    ).json()
    assert overdue_task["is_overdue"] is True
    assert overdue_task["is_due_soon"] is False

    due_soon_task = client.post(
        "/tasks/",
        json={
            "title": "Bài sắp đến hạn của A",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "IN_PROGRESS",
            "subject_id": sub_a["id"],
        },
        headers=headers_a,
    ).json()
    assert due_soon_task["is_overdue"] is False
    assert due_soon_task["is_due_soon"] is True

    # Kiểm tra Data Isolation: User B không thấy và không thể tác động dữ liệu của User A
    assert client.get("/subjects/", headers=headers_b).json() == []
    assert client.get("/tasks/", headers=headers_b).json() == []
    assert client.post("/tasks/", json={"title": "Hack", "subject_id": sub_a["id"]}, headers=headers_b).status_code == 404
    assert client.put(f"/tasks/{overdue_task['id']}", json={"title": "Sửa trộm"}, headers=headers_b).status_code == 404
    assert client.patch(f"/tasks/{overdue_task['id']}/status", json={"status": "DONE"}, headers=headers_b).status_code == 404
    assert client.delete(f"/tasks/{overdue_task['id']}", headers=headers_b).status_code == 404