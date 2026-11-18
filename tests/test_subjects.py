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
    """Tạo user mẫu tương thích với các cột hiện có của bảng users."""
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
def client_with_users(db_session):
    """Cung cấp TestClient kèm 2 tài khoản (User A và User B) để test phân quyền."""
    user_a = make_user(db_session, 1, "a")
    user_b = make_user(db_session, 2, "b")

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
        yield client, db_session, user_a, user_b, active_user

    app.dependency_overrides.clear()


# 1. CREATE - Tạo môn học hợp lệ
def test_create_subject_success(client_with_users):
    client, _, _, _, _ = client_with_users
    payload = {
        "code": "INT3306",
        "name": "Phát triển ứng dụng Web",
        "description": "Môn học thực tập nhóm"
    }
    response = client.post("/subjects/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "INT3306"
    assert data["name"] == "Phát triển ứng dụng Web"
    assert "id" in data


# 2. CREATE - Validate dữ liệu đầu vào không hợp lệ
def test_create_subject_validation_error(client_with_users):
    client, _, _, _, _ = client_with_users
    # Gửi thiếu trường name bắt buộc
    response = client.post("/subjects/", json={"code": ""})
    assert response.status_code == 422


# 3. READ - Lấy danh sách môn học của user đang đăng nhập
def test_get_subjects_list(client_with_users):
    client, _, _, _, _ = client_with_users
    client.post("/subjects/", json={"code": "BAS1150", "name": "Triết học Mác - Lênin"})
    client.post("/subjects/", json={"code": "INT1332", "name": "Lập trình hướng đối tượng"})

    response = client.get("/subjects/")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) == 2
    assert subjects[0]["code"] == "BAS1150"
    assert subjects[1]["code"] == "INT1332"


# 4. UPDATE - Cập nhật thông tin môn học
def test_update_subject_success(client_with_users):
    client, _, _, _, _ = client_with_users
    create_res = client.post("/subjects/", json={"code": "INT1434", "name": "Lập trình Web cũ"})
    subject_id = create_res.json()["id"]

    update_res = client.put(
        f"/subjects/{subject_id}",
        json={"code": "INT1434", "name": "Lập trình Web Nâng Cao"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Lập trình Web Nâng Cao"


# 5. DATA ISOLATION - Chặn User B truy cập/sửa/xóa môn học của User A
def test_subject_data_isolation(client_with_users):
    client, _, user_a, user_b, active_user = client_with_users

    # User A tạo môn học
    active_user["current"] = user_a
    create_res = client.post("/subjects/", json={"code": "SEC101", "name": "An toàn bảo mật"})
    subject_id = create_res.json()["id"]

    # Chuyển sang User B
    active_user["current"] = user_b

    # User B xem danh sách -> không thấy môn của User A
    list_res = client.get("/subjects/")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 0

    # User B cố tình sửa môn của User A -> 404
    put_res = client.put(f"/subjects/{subject_id}", json={"code": "HACK", "name": "Sửa trộm"})
    assert put_res.status_code == 404

    # User B cố tình xóa môn của User A -> 404
    del_res = client.delete(f"/subjects/{subject_id}")
    assert del_res.status_code == 404


# 6. DELETE CONSTRAINT - Chặn xóa môn học khi vẫn còn bài tập (Task) liên kết
def test_delete_subject_blocked_when_has_tasks(client_with_users):
    client, db, _, _, _ = client_with_users

    # Tạo môn học
    create_res = client.post("/subjects/", json={"code": "SE104", "name": "Công nghệ phần mềm"})
    subject_id = create_res.json()["id"]

    # Thêm 1 bài tập gắn vào môn học này
    task = Task(title="Viết tài liệu SRS", status="TODO", subject_id=subject_id)
    db.add(task)
    db.commit()

    # Thử xóa môn học -> hệ thống phải chặn (400 hoặc 409)
    del_blocked = client.delete(f"/subjects/{subject_id}")
    assert del_blocked.status_code in (400, 409)


# 7. DELETE SUCCESS - Xóa môn học thành công khi không có bài tập liên kết
def test_delete_subject_success(client_with_users):
    client, _, _, _, _ = client_with_users

    create_res = client.post("/subjects/", json={"code": "ENG201", "name": "Tiếng Anh chuyên ngành"})
    subject_id = create_res.json()["id"]

    del_res = client.delete(f"/subjects/{subject_id}")
    assert del_res.status_code in (200, 204)

    # Kiểm tra lại danh sách phải rỗng
    list_res = client.get("/subjects/")
    assert len(list_res.json()) == 0