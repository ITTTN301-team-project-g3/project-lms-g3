from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.database import engine, Base
from app.routers import auth, subject, task, dashboard
from fastapi.middleware.cors import CORSMiddleware
# Import các models để SQLAlchemy nhận diện và tạo bảng tự động
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task

# Khởi tạo tự động các bảng MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Project Manager API",
    description="API Quản lý dự án nhóm - Sprint 2",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn gọi vào (hoặc chỉ định ["http://127.0.0.1:5500"])
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép mọi phương thức (GET, POST, PUT, DELETE,...)
    allow_headers=["*"],  # Cho phép mọi header (bao gồm cả Authorization chứa Token)
)

# 1. Đăng ký Router Auth, Subject & from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import Base, engine

# Import các models để SQLAlchemy nhận diện và tạo bảng tự động
from app.models.subject import Subject
from app.models.task import Task
from app.models.user import User
from app.routers import auth, dashboard, subject, task

# Khởi tạo tự động các bảng MySQL
Base.metadata.create_all(bind=engine)

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
    allow_origins=["*"],  # Cho phép tất cả các nguồn gọi vào (hoặc chỉ định ["http://127.0.0.1:5500"])
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép mọi phương thức (GET, POST, PUT, DELETE,...)
    allow_headers=["*"],  # Cho phép mọi header (bao gồm cả Authorization chứa Token)
)

# 1. Đăng ký Router Auth, Subject & Task
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
# Update check task module
app.include_router(auth.router)
app.include_router(subject.router)
app.include_router(task.router)
app.include_router(dashboard.router)

# 2. Mount thư mục tĩnh static chứa html/css/js
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "Server FastAPI hoạt động tốt!"}
# Update check task module

