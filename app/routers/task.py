from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db  # Đã sửa lại đường dẫn import đúng với dự án
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskResponse
from app.routers.auth import get_current_user  # Hàm lấy user từ token hiện tại

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.get("/", response_model=List[TaskResponse])
def get_user_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Lọc danh sách bài tập thuộc tài khoản đang đăng nhập
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks