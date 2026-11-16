from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.database import engine, Base
from app.routers import auth, subject, task  # 1. Thêm 'task' vào đây
# Import các models để SQLAlchemy nhận diện và tạo bảng tự động
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task  # 1. Thêm import model Task ở đây

# Khởi tạo tự động các bảng MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Project Manager API",
    description="API Quản lý dự án nhóm - Sprint 1",
    version="1.0.0"
)

# 1. Đăng ký Router Auth, Subject & Task
app.include_router(auth.router)
app.include_router(subject.router)
app.include_router(task.router)  # 2. Thêm dòng đăng ký router task ở đây

# 2. Mount thư mục tĩnh static chứa HTML/CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "Server FastAPI hoạt động tốt cho Ngày 2!"}