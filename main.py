from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.database import engine, Base
from app.routers import auth, subject  # 1. Thêm 'subject' vào đây
# Import các models để SQLAlchemy nhận diện và tạo bảng tự động
from app.models.user import User
from app.models.subject import Subject

# Khởi tạo tự động các bảng MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Project Manager API",
    description="API Quản lý dự án nhóm - Sprint 1",
    version="1.0.0"
)

# 1. Đăng ký Router Auth & Subject
app.include_router(auth.router)
app.include_router(subject.router)  # 2. Thêm dòng đăng ký router subject ở đây

# 2. Mount thư mục tĩnh static chứa HTML/CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "Server FastAPI hoạt động tốt cho Ngày 2!"}