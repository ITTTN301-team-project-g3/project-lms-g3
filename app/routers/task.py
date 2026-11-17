from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Import kết nối database và các models/schemas liên quan
from app.db.database import get_db
from app.models.task import Task, StatusEnum
from app.models.subject import Subject
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# 1. API Xem danh sách bài tập (GET /tasks/)
@router.get("/", response_model=List[TaskResponse], summary="Xem danh sách bài tập")
def get_tasks(
    subject_id: Optional[int] = None,
    task_status: Optional[StatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Chỉ lấy bài tập của tài khoản đang đăng nhập
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if subject_id:
        query = query.filter(Task.subject_id == subject_id)
    if task_status:
        query = query.filter(Task.status == task_status)
    return query.all()

# 2. API Tạo bài tập mới (POST /tasks/)
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Thêm bài tập mới")
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Kiểm tra môn học có tồn tại và thuộc về user đang đăng nhập không
    subject = db.query(Subject).filter(
        Subject.id == task_in.subject_id,
        Subject.user_id == current_user.id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học hoặc bạn không có quyền thêm bài tập vào môn học này!"
        )

    # Bước 2: Khởi tạo bài tập mới gắn kèm user_id
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        subject_id=task_in.subject_id,
        user_id=current_user.id
    )

    # Bước 3: Lưu vào Database
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

# 3. API Cập nhật bài tập (PUT /tasks/{task_id})
@router.put("/{task_id}", response_model=TaskResponse, summary="Cập nhật thông tin bài tập")
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập theo ID và kiểm tra quyền sở hữu
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền chỉnh sửa bài tập này!"
        )

    # Bước 2: Nếu đổi môn học, kiểm tra môn học mới có thuộc user không
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

    # Bước 3: Cập nhật các trường được gửi lên
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "subject_id":
            setattr(task, field, value)

    # Bước 4: Lưu vào Database
    db.commit()
    db.refresh(task)

    return task

# 4. API Xóa bài tập (DELETE /tasks/{task_id})
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa bài tập")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập của đúng user đang đăng nhập
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    # Bước 2: Không tìm thấy hoặc không phải của user thì báo lỗi 404
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền xóa!"
        )

    # Bước 3: Xóa khỏi Database và trả về mã 204
    db.delete(task)
    db.commit()
    return None


# 5. API Cập nhật trạng thái bài tập (PATCH /tasks/{task_id}/status)
@router.patch("/{task_id}/status", response_model=TaskResponse, summary="Cập nhật trạng thái bài tập")
def update_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập theo ID và kiểm tra xem có đúng của người đang đăng nhập không
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    # Bước 2: Nếu không tìm thấy hoặc không phải bài tập của mình thì báo lỗi 404
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền cập nhật!"
        )

    #Bước 3: Cập nhật trạng thái mới (TODO, IN_PROGRESS, hoặc DONE) và lưu vào Database
    task.status = status_in.status.value
    db.commit()
    db.refresh(task)

    return task