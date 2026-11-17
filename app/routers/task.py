from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.task import Task
from app.models.subject import Subject
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# 1. API Xem danh sách bài tập (có hỗ trợ lọc theo môn học và trạng thái)
@router.get("/", response_model=List[TaskResponse], summary="Xem danh sách bài tập")
def get_tasks(
    subject_id: Optional[int] = None,
    task_status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).join(Subject).filter(Subject.user_id == current_user.id)
    if subject_id is not None:
        query = query.filter(Task.subject_id == subject_id)
    if task_status is not None:
        query = query.filter(Task.status == task_status)
    return query.all()

# 2. API Tạo bài tập mới
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Thêm bài tập mới")
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subject = db.query(Subject).filter(
        Subject.id == task_in.subject_id,
        Subject.user_id == current_user.id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học hoặc bạn không có quyền thêm bài tập vào môn học này!"
        )

    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        subject_id=task_in.subject_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# 3. API Cập nhật bài tập
@router.put("/{task_id}", response_model=TaskResponse, summary="Cập nhật thông tin bài tập")
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .join(Subject)
        .filter(Task.id == task_id, Subject.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền chỉnh sửa bài tập này!"
        )

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

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "subject_id":
            setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

# 4. API Xóa bài tập
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa bài tập")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .join(Subject)
        .filter(Task.id == task_id, Subject.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền xóa!"
        )

    db.delete(task)
    db.commit()
    return None