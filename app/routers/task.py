from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.task import Task
from app.models.subject import Subject
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# 1. API Xem danh sách bài tập của user đang đăng nhập
@router.get("/", response_model=List[TaskResponse], summary="Xem danh sách bài tập")
def get_user_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Lọc danh sách bài tập thuộc tài khoản đang đăng nhập
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

# 2. API Tạo bài tập mới
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

    # Bước 2: Khởi tạo đối tượng bài tập mới (gắn kèm user_id của user hiện tại)
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        subject_id=task_in.subject_id,
        user_id=current_user.id
    )

    # Bước 3: Lưu vào MySQL và refresh
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

# 3. API Cập nhật bài tập (Update Task)
@router.put("/{task_id}", response_model=TaskResponse, summary="Cập nhật thông tin bài tập")
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập theo ID và kiểm tra quyền sở hữu của user
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền chỉnh sửa bài tập này!"
        )

    # Bước 2: Nếu người dùng muốn đổi sang môn học khác, kiểm tra môn học mới
    if task_in.subject_id is not None:
        subject = db.query(Subject).filter(
            Subject.id == task_in.subject_id,
            Subject.user_id == current_user.id
        ).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy môn học mới hoặc bạn không sở hữu môn học này!"
            )
        task.subject_id = task_in.subject_id

    # Bước 3: Cập nhật các trường được truyền lên (bỏ qua giá trị None)
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "subject_id":
            setattr(task, field, value)

    # Bước 4: Lưu vào MySQL
    db.commit()
    db.refresh(task)

    return task