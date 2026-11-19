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

# 1. Đăng ký Router Auth, Subject & Task
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

