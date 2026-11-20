import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, ensure_performance_indexes
from app.core.dependencies import get_current_user
from app.db.database import Base, get_db
from app.models.subject import Subject
from app.models.task import StatusEnum, Task
from app.models.user import User

MAX_RESPONSE_TIME_SEC = 2.0  # Ngưỡng yêu cầu phi chức năng NFR-07 (< 2 giây)
SAMPLE_SUBJECT_COUNT = 10
SAMPLE_TASK_COUNT = 500

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def perf_client():
    Base.metadata.create_all(bind=engine)
    ensure_performance_indexes(engine)
    db = TestingSessionLocal()

    user = User(
        id=1,
        full_name="Sinh Viên Kiểm Thử Hiệu Năng",
        email="perf_nfr07@studenthub.edu.vn",
        password_hash="hashed_secret_123",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Khởi tạo 10 môn học mẫu
    subjects = [
        Subject(code=f"IT{100 + i}", name=f"Học phần chuyên ngành {i + 1}", user_id=user.id)
        for i in range(SAMPLE_SUBJECT_COUNT)
    ]
    db.add_all(subjects)
    db.commit()
    for sub in subjects:
        db.refresh(sub)

    # Khởi tạo 500 bài tập mẫu đa dạng trạng thái và mốc hạn nộp
    now = datetime.now()
    statuses = [StatusEnum.TODO, StatusEnum.IN_PROGRESS, StatusEnum.DONE]
    tasks = []
    for idx in range(SAMPLE_TASK_COUNT):
        sub = subjects[idx % SAMPLE_SUBJECT_COUNT]
        st = statuses[idx % 3]
        due = now + timedelta(days=(idx % 15) - 5)
        tasks.append(
            Task(
                title=f"Bài tập thực hành số {idx + 1} - Tuần {(idx % 12) + 1}",
                description=f"Mô tả chi tiết bài tập mẫu thứ {idx + 1} phục vụ đo hiệu năng NFR-07.",
                due_date=due,
                status=st,
                subject_id=sub.id,
            )
        )
    db.bulk_save_objects(tasks)
    db.commit()

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
        yield client, subjects[0].id

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


# 1. Xác nhận các index tối ưu đã được tạo trên bảng subjects và tasks
def test_database_performance_indexes_exist(perf_client):
    inspector = inspect(engine)
    subject_indexes = {idx["name"] for idx in inspector.get_indexes("subjects")}
    task_indexes = {idx["name"] for idx in inspector.get_indexes("tasks")}

    assert "idx_subjects_user_id" in subject_indexes
    assert "idx_tasks_subject_status" in task_indexes
    assert "idx_tasks_due_date" in task_indexes


# 2. Đo thời gian phản hồi API danh sách bài tập (GET /tasks/ với 500 bản ghi)
def test_nfr07_tasks_list_and_filter_response_time(perf_client):
    client, first_subject_id = perf_client

    # Đo GET /tasks/ toàn bộ 500 bài tập
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        res = client.get("/tasks/")
        elapsed = time.perf_counter() - start
        assert res.status_code == 200
        assert len(res.json()) == SAMPLE_TASK_COUNT
        assert "X-Process-Time" in res.headers
        durations.append(elapsed)

    avg_list_sec = sum(durations) / len(durations)
    max_list_sec = max(durations)
    print(f"\n[NFR-07] GET /tasks/ (500 items) -> Avg: {avg_list_sec * 1000:.2f} ms | Max: {max_list_sec * 1000:.2f} ms")
    assert max_list_sec < MAX_RESPONSE_TIME_SEC

    # Đo GET /tasks/ có tìm kiếm + lọc theo môn học và trạng thái
    start_filter = time.perf_counter()
    res_filter = client.get(f"/tasks/?search=Tuần 1&subject_id={first_subject_id}&status=TODO")
    filter_elapsed = time.perf_counter() - start_filter
    assert res_filter.status_code == 200
    print(f"[NFR-07] GET /tasks/ (Filtered)  -> Time: {filter_elapsed * 1000:.2f} ms")
    assert filter_elapsed < MAX_RESPONSE_TIME_SEC


# 3. Đo thời gian phản hồi API thống kê Dashboard (GET /dashboard/stats trên 500 bản ghi)
def test_nfr07_dashboard_stats_response_time(perf_client):
    client, _ = perf_client

    durations = []
    for _ in range(5):
        start = time.perf_counter()
        res = client.get("/dashboard/stats")
        elapsed = time.perf_counter() - start
        assert res.status_code == 200
        data = res.json()
        assert data["total_subjects"] == SAMPLE_SUBJECT_COUNT
        assert data["total_tasks"] == SAMPLE_TASK_COUNT
        assert "X-Process-Time" in res.headers
        durations.append(elapsed)

    avg_dash_sec = sum(durations) / len(durations)
    max_dash_sec = max(durations)
    print(f"\n[NFR-07] GET /dashboard/stats    -> Avg: {avg_dash_sec * 1000:.2f} ms | Max: {max_dash_sec * 1000:.2f} ms")
    assert max_dash_sec < MAX_RESPONSE_TIME_SEC