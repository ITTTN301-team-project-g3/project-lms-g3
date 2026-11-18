import os
import sys

# Thêm thư mục gốc dự án vào sys.path để chạy trực tiếp lệnh pytest không bị lỗi import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.db.database import Base, get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task

# Khởi tạo Database SQLite trong bộ nhớ dành riêng cho môi trường Test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def make_user(db, user_id: int, suffix: str) -> User:
    """Tạo user mẫu tương thích với bảng users hiện tại."""
    cols = set(User.__table__.columns.keys())
    data = {"id": user_id}
    if "username" in cols:
        data["username"] = f"sv_{suffix}"
    if "email" in cols:
        data["email"] = f"sv_{suffix}@studenthub.edu.vn"
    if "full_name" in cols:
        data["full_name"] = f"Sinh Viên {suffix.upper()}"
    if "password_hash" in cols:
        data["password_hash"] = "hashed_secret_123"
    elif "hashed_password" in cols:
        data["hashed_password"] = "hashed_secret_123"
    elif "password" in cols:
        data["password"] = "hashed_secret_123"

    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_subject(db, user_id: int, code: str, name: str) -> Subject:
    """Tạo môn học mẫu thuộc về user chỉ định."""
    subject = Subject(code=code, name=name, user_id=user_id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client_with_data(db_session):
    """Cung cấp TestClient kèm 2 user và các môn học mẫu."""
    user_a = make_user(db_session, 1, "a")
    user_b = make_user(db_session, 2, "b")

    sub_a1 = make_subject(db_session, user_a.id, "INT3306", "Phát triển ứng dụng Web")
    sub_a2 = make_subject(db_session, user_a.id, "SE104", "Công nghệ phần mềm")
    sub_b1 = make_subject(db_session, user_b.id, "SEC101", "An toàn bảo mật")

    active_user = {"current": user_a}

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return active_user["current"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client, db_session, user_a, user_b, sub_a1, sub_a2, sub_b1, active_user

    app.dependency_overrides.clear()


# 1. CREATE - Tạo bài tập mới hợp lệ
def test_create_task_success(client_with_data):
    client, _, _, _, sub_a1, _, _, _ = client_with_data
    payload = {
        "title": "Hoàn thành API CRUD Bài tập",
        "description": "Viết router và schema cho module task",
        "due_date": "2026-11-25T23:59:00",
        "status": "TODO",
        "subject_id": sub_a1.id
    }
    response = client.post("/tasks/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hoàn thành API CRUD Bài tập"
    assert data["status"] == "TODO"
    assert data["subject_id"] == sub_a1.id
    assert "id" in data


# 2. CREATE - Validate dữ liệu đầu vào sai chuẩn
def test_create_task_validation_error(client_with_data):
    client, _, _, _, sub_a1, _, _, _ = client_with_data
    # Gửi trạng thái không nằm trong Literal["TODO", "IN_PROGRESS", "DONE"]
    bad_payload = {
        "title": "Bài tập test lỗi",
        "status": "INVALID_STATUS",
        "subject_id": sub_a1.id
    }
    response = client.post("/tasks/", json=bad_payload)
    assert response.status_code == 422


# 3. CREATE SECURITY - Chặn tạo bài tập vào môn học của người khác hoặc môn không tồn tại
def test_create_task_forbidden_subject(client_with_data):
    client, _, _, _, _, _, sub_b1, _ = client_with_data

    # User A cố tạo bài tập vào môn của User B
    res_other = client.post("/tasks/", json={
        "title": "Chèn trộm bài tập",
        "subject_id": sub_b1.id
    })
    assert res_other.status_code == 404

    # Tạo bài tập vào subject_id không tồn tại
    res_not_found = client.post("/tasks/", json={
        "title": "Bài tập môn ảo",
        "subject_id": 9999
    })
    assert res_not_found.status_code == 404


# 4. READ & FILTER - Lấy danh sách bài tập và lọc theo môn học / trạng thái
def test_get_tasks_and_filters(client_with_data):
    client, _, _, _, sub_a1, sub_a2, _, _ = client_with_data

    client.post("/tasks/", json={"title": "Task 1", "status": "TODO", "subject_id": sub_a1.id})
    client.post("/tasks/", json={"title": "Task 2", "status": "DONE", "subject_id": sub_a1.id})
    client.post("/tasks/", json={"title": "Task 3", "status": "IN_PROGRESS", "subject_id": sub_a2.id})

    # Lấy tất cả bài tập của User A -> 3 bài
    res_all = client.get("/tasks/")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # Lọc theo môn sub_a1 -> 2 bài
    res_sub = client.get(f"/tasks/?subject_id={sub_a1.id}")
    assert len(res_sub.json()) == 2

    # Lọc theo trạng thái DONE -> 1 bài
    res_status = client.get("/tasks/?task_status=DONE")
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["title"] == "Task 2"

    # Kết hợp lọc theo môn sub_a1 và trạng thái TODO -> 1 bài
    res_combo = client.get(f"/tasks/?subject_id={sub_a1.id}&task_status=TODO")
    assert len(res_combo.json()) == 1
    assert res_combo.json()[0]["title"] == "Task 1"


# 5. UPDATE - Cập nhật thông tin, trạng thái và chuyển môn học hợp lệ
def test_update_task_success(client_with_data):
    client, _, _, _, sub_a1, sub_a2, _, _ = client_with_data

    create_res = client.post("/tasks/", json={
        "title": "Báo cáo tuần 1",
        "status": "TODO",
        "subject_id": sub_a1.id
    })
    task_id = create_res.json()["id"]

    update_res = client.put(f"/tasks/{task_id}", json={
        "title": "Báo cáo tuần 1 (Đã hoàn thiện)",
        "status": "DONE",
        "subject_id": sub_a2.id
    })

    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Báo cáo tuần 1 (Đã hoàn thiện)"
    assert updated["status"] == "DONE"
    assert updated["subject_id"] == sub_a2.id


# 6. DATA ISOLATION - Chặn User B xem, sửa, xóa bài tập của User A
def test_task_data_isolation(client_with_data):
    client, _, user_a, user_b, sub_a1, _, _, active_user = client_with_data

    # User A tạo bài tập
    active_user["current"] = user_a
    create_res = client.post("/tasks/", json={
        "title": "Bài tập riêng của User A",
        "subject_id": sub_a1.id
    })
    task_id = create_res.json()["id"]

    # Chuyển sang User B
    active_user["current"] = user_b

    # User B xem danh sách -> rỗng
    list_res = client.get("/tasks/")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 0

    # User B cố sửa bài của User A -> 404
    put_res = client.put(f"/tasks/{task_id}", json={"status": "DONE"})
    assert put_res.status_code == 404

    # User B cố xóa bài của User A -> 404
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 404


# 7. DELETE - Xóa bài tập thành công
def test_delete_task_success(client_with_data):
    client, _, _, _, sub_a1, _, _, _ = client_with_data

    create_res = client.post("/tasks/", json={
        "title": "Bài tập nháp cần xóa",
        "subject_id": sub_a1.id
    })
    task_id = create_res.json()["id"]

    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    # Kiểm tra lại danh sách phải rỗng
    list_res = client.get("/tasks/")
    assert len(list_res.json()) == 0