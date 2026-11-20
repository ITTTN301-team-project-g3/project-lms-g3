import os
import sys
from datetime import datetime, timedelta

# Thêm thư mục gốc dự án vào sys.path để chạy trực tiếp lệnh pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.db.database import Base, get_db
from app.core.dependencies import get_current_user
from app.core.task_overdue import is_task_overdue
from app.core.task_due_soon import is_task_due_soon
from app.models.user import User
from app.models.subject import Subject

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def make_user(db, user_id: int = 1) -> User:
    """Khởi tạo user mẫu tương thích với cấu trúc bảng users hiện tại."""
    cols = set(User.__table__.columns.keys())
    data = {"id": user_id}
    if "username" in cols:
        data["username"] = "sv_deadline_test"
    if "email" in cols:
        data["email"] = "deadline_test@studenthub.edu.vn"
    if "full_name" in cols:
        data["full_name"] = "Sinh Viên Kiểm Thử Hạn Nộp"
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
def client_with_subject():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    user = make_user(db, user_id=1)
    subject = Subject(code="SE104", name="Công nghệ phần mềm", user_id=user.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client, subject

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


# =====================================================================
# PHẦN A: UNIT TEST TRỰC TIẾP HÀM CORE (is_task_overdue & is_task_due_soon)
# =====================================================================

def test_core_deadline_functions():
    now = datetime.now()
    past_dt = now - timedelta(days=1)
    today_dt = now + timedelta(hours=1)
    two_days_dt = now + timedelta(days=2)
    far_dt = now + timedelta(days=7)

    # 1. Quá khứ (TODO) -> quá hạn = True, sắp đến hạn = False
    assert is_task_overdue(past_dt, "TODO") is True
    assert is_task_due_soon(past_dt, "TODO") is False

    # 2. Hôm nay (IN_PROGRESS) -> quá hạn = False, sắp đến hạn = True
    assert is_task_overdue(today_dt, "IN_PROGRESS") is False
    assert is_task_due_soon(today_dt, "IN_PROGRESS") is True

    # 3. 2 ngày tới (TODO) -> quá hạn = False, sắp đến hạn = True
    assert is_task_overdue(two_days_dt, "TODO") is False
    assert is_task_due_soon(two_days_dt, "TODO") is True

    # 4. Còn 7 ngày -> cả hai đều False
    assert is_task_overdue(far_dt, "TODO") is False
    assert is_task_due_soon(far_dt, "TODO") is False

    # 5. Đã hoàn thành (DONE) dù quá khứ hay hôm nay -> đều False
    assert is_task_overdue(past_dt, "DONE") is False
    assert is_task_due_soon(today_dt, "DONE") is False


# =====================================================================
# PHẦN B: INTEGRATION TEST QUA API VỚI CÁC MỐC DỮ LIỆU MẪU
# =====================================================================

# 1. Mốc quá khứ (chưa DONE) -> Báo quá hạn (is_overdue = True)
def test_api_task_past_deadline_is_overdue(client_with_subject):
    client, subject = client_with_subject
    past_due = (datetime.now() - timedelta(days=2)).isoformat()

    res = client.post("/tasks/", json={
        "title": "Bài tập mốc quá khứ",
        "due_date": past_due,
        "status": "TODO",
        "subject_id": subject.id
    })

    assert res.status_code == 201
    data = res.json()
    assert data["is_overdue"] is True
    assert data["is_due_soon"] is False


# 2. Mốc hôm nay (còn hạn trong ngày) -> Báo sắp đến hạn (is_due_soon = True)
def test_api_task_today_deadline_is_due_soon(client_with_subject):
    client, subject = client_with_subject
    today_due = (datetime.now() + timedelta(hours=2)).isoformat()

    res = client.post("/tasks/", json={
        "title": "Bài tập mốc hôm nay",
        "due_date": today_due,
        "status": "IN_PROGRESS",
        "subject_id": subject.id
    })

    assert res.status_code == 201
    data = res.json()
    assert data["is_overdue"] is False
    assert data["is_due_soon"] is True


# 3. Mốc 2 ngày tới -> Báo sắp đến hạn (is_due_soon = True)
def test_api_task_two_days_ahead_is_due_soon(client_with_subject):
    client, subject = client_with_subject
    two_days_due = (datetime.now() + timedelta(days=2)).isoformat()

    res = client.post("/tasks/", json={
        "title": "Bài tập mốc 2 ngày tới",
        "due_date": two_days_due,
        "status": "TODO",
        "subject_id": subject.id
    })

    assert res.status_code == 201
    data = res.json()
    assert data["is_overdue"] is False
    assert data["is_due_soon"] is True


# 4. Mốc dài hạn (> 3 ngày) và bài không có hạn nộp -> Không cảnh báo
def test_api_task_safe_or_no_deadline(client_with_subject):
    client, subject = client_with_subject
    safe_due = (datetime.now() + timedelta(days=10)).isoformat()

    res_safe = client.post("/tasks/", json={
        "title": "Bài tập còn 10 ngày",
        "due_date": safe_due,
        "status": "TODO",
        "subject_id": subject.id
    })
    assert res_safe.status_code == 201
    assert res_safe.json()["is_overdue"] is False
    assert res_safe.json()["is_due_soon"] is False

    res_none = client.post("/tasks/", json={
        "title": "Bài tập không đặt hạn chót",
        "due_date": None,
        "status": "TODO",
        "subject_id": subject.id
    })
    assert res_none.status_code == 201
    assert res_none.json()["is_overdue"] is False
    assert res_none.json()["is_due_soon"] is False


# 5. Đổi trạng thái bài quá hạn sang DONE -> Tự động tắt cảnh báo
def test_api_completed_task_clears_warning(client_with_subject):
    client, subject = client_with_subject
    past_due = (datetime.now() - timedelta(days=3)).isoformat()

    create_res = client.post("/tasks/", json={
        "title": "Bài tập trễ hạn vừa hoàn thành",
        "due_date": past_due,
        "status": "TODO",
        "subject_id": subject.id
    })
    task_id = create_res.json()["id"]
    assert create_res.json()["is_overdue"] is True

    patch_res = client.patch(f"/tasks/{task_id}/status", json={"status": "DONE"})
    assert patch_res.status_code == 200
    assert patch_res.json()["is_overdue"] is False
    assert patch_res.json()["is_due_soon"] is False


# 6. Kiểm tra tổng hợp danh sách GET /tasks/ với bộ dữ liệu mẫu đủ 4 trường hợp
def test_api_get_tasks_list_with_mixed_sample_data(client_with_subject):
    client, subject = client_with_subject
    now = datetime.now()

    samples = [
        {"title": "Mẫu 1 - Quá khứ", "due_date": (now - timedelta(days=1)).isoformat(), "status": "TODO"},
        {"title": "Mẫu 2 - Hôm nay", "due_date": (now + timedelta(hours=1)).isoformat(), "status": "IN_PROGRESS"},
        {"title": "Mẫu 3 - 2 ngày tới", "due_date": (now + timedelta(days=2)).isoformat(), "status": "TODO"},
        {"title": "Mẫu 4 - Đã xong", "due_date": (now - timedelta(days=5)).isoformat(), "status": "DONE"},
    ]

    for item in samples:
        res = client.post("/tasks/", json={**item, "subject_id": subject.id})
        assert res.status_code == 201

    list_res = client.get("/tasks/")
    assert list_res.status_code == 200
    tasks_by_title = {t["title"]: t for t in list_res.json()}

    assert tasks_by_title["Mẫu 1 - Quá khứ"]["is_overdue"] is True
    assert tasks_by_title["Mẫu 1 - Quá khứ"]["is_due_soon"] is False

    assert tasks_by_title["Mẫu 2 - Hôm nay"]["is_overdue"] is False
    assert tasks_by_title["Mẫu 2 - Hôm nay"]["is_due_soon"] is True

    assert tasks_by_title["Mẫu 3 - 2 ngày tới"]["is_overdue"] is False
    assert tasks_by_title["Mẫu 3 - 2 ngày tới"]["is_due_soon"] is True

    assert tasks_by_title["Mẫu 4 - Đã xong"]["is_overdue"] is False
    assert tasks_by_title["Mẫu 4 - Đã xong"]["is_due_soon"] is False