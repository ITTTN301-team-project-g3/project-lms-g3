import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.db.database import Base, engine
from app.models.subject import Subject
from app.models.task import Task
from app.models.user import User
from app.routers import auth, dashboard, subject, task


def ensure_performance_indexes(target_engine) -> list[str]:
    """Kiểm tra và tạo các index tối ưu truy vấn cho MySQL/SQLite nếu chưa tồn tại."""
    created = []
    index_specs = [
        ("subjects", "idx_subjects_user_id", ["user_id"]),
        ("tasks", "idx_tasks_subject_status", ["subject_id", "status"]),
        ("tasks", "idx_tasks_due_date", ["due_date"]),
    ]
    try:
        inspector = inspect(target_engine)
        existing_tables = set(inspector.get_table_names())

        with target_engine.begin() as conn:
            for table_name, index_name, columns in index_specs:
                if table_name not in existing_tables:
                    continue
                table_cols = {col["name"] for col in inspector.get_columns(table_name)}
                if not all(col in table_cols for col in columns):
                    continue
                existing_indexes = {idx["name"] for idx in inspector.get_indexes(table_name)}
                if index_name not in existing_indexes:
                    cols_sql = ", ".join(columns)
                    conn.execute(text(f"CREATE INDEX {index_name} ON {table_name} ({cols_sql})"))
                    created.append(index_name)
    except Exception as exc:
        print(f"[DB Index Notice] Bỏ qua tạo index tự động: {exc}")
    return created


# Khởi tạo tự động các bảng MySQL và index tối ưu hiệu năng
Base.metadata.create_all(bind=engine)
ensure_performance_indexes(engine)

tags_metadata = [
    {
        "name": "Auth",
        "description": "Đăng ký, đăng nhập và xác thực người dùng bằng JWT Bearer Token.",
    },
    {
        "name": "Subjects",
        "description": "Quản lý danh sách môn học / dự án và thông tin liên quan.",
    },
    {
        "name": "Tasks",
        "description": (
            "Quản lý bài tập/công việc, cập nhật trạng thái (`TODO`, `IN_PROGRESS`, `DONE`), "
            "cùng logic tự động tính toán **Quá hạn (`is_overdue`)** và **Sắp đến hạn (`is_due_soon`)**."
        ),
    },
    {
        "name": "Dashboard",
        "description": "Tổng hợp số liệu thống kê tổng quan cho giao diện Dashboard.",
    },
]

api_description = """
## Hệ thống Quản lý Dự án & Bài tập Nhóm (Project LMS)

Tài liệu API tự động phục vụ kiểm thử và tích hợp frontend/backend:
- **Xác thực JWT:** Sử dụng Bearer Token cho các endpoint yêu cầu đăng nhập.
- **Trạng thái bài tập:** Hỗ trợ theo dõi trạng thái xử lý và tự động đánh dấu bài tập quá hạn hoặc sắp đến hạn (trong 3 ngày tới).
- **Tài liệu tương tác:** Xem thử nghiệm trực tiếp tại `/docs` (Swagger UI) hoặc đọc cấu trúc chi tiết tại `/redoc` (ReDoc).
"""

app = FastAPI(
    title="Project LMS API",
    description=api_description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Nhóm phát triển Project LMS (G3)",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def measure_response_time_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f} ms"
    return response


# 1. Đăng ký Router Auth, Subject, Task & Dashboard
app.include_router(auth.router)
app.include_router(subject.router)
app.include_router(task.router)
app.include_router(dashboard.router)

# 2. Mount thư mục tĩnh static chứa html/css/js
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get(
    "/",
    summary="Kiểm tra trạng thái máy chủ",
    description="Endpoint kiểm tra nhanh xem dịch vụ FastAPI có đang hoạt động bình thường hay không.",
    tags=["Health Check"],
)
def root():
    return {"message": "Server FastAPI hoạt động tốt!"}