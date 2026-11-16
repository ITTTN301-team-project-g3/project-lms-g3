from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.task import Task
from app.models.subject import Subject
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# 1. API Tạo bài tập mới
# Đường dẫn: POST /tasks/
# Status Code: 201 Created
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Thêm bài tập mới")
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Kiểm tra môn học có tồn tại và thuộc sở hữu của user đang đăng nhập không
    subject = db.query(Subject).filter(
        Subject.id == task_in.subject_id,
        Subject.user_id == current_user.id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học hoặc bạn không có quyền thêm bài tập vào môn học này!"
        )

    # Bước 2: Khởi tạo đối tượng bài tập mới
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        subject_id=task_in.subject_id
    )

    # Bước 3: Lưu vào MySQL và refresh để lấy ID vừa khởi tạo
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task