from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import kết nối database và các models/schemas liên quan
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

# Schema nhận dữ liệu trạng thái mới khi gọi API PATCH
class TaskStatusUpdate(BaseModel):
    status: TaskStatus


# 1. API Xem, Tìm kiếm và Lọc danh sách bài tập (GET /tasks/)
@router.get("/", response_model=List[TaskResponse], summary="Xem, tìm kiếm và lọc danh sách bài tập")
def get_tasks(
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    task_status: Optional[TaskStatus] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Luôn nối với bảng Subject để chỉ lấy bài tập thuộc tài khoản đang đăng nhập
    query = db.query(Task).join(Subject).filter(Subject.user_id == current_user.id)

    # Nếu có nhập từ khóa -> tìm trong tiêu đề bài tập (không phân biệt chữ hoa/thường)
    if search and search.strip():
        query = query.filter(Task.title.ilike(f"%{search.strip()}%"))

    # Nếu có chọn môn học -> lọc đúng môn học đó
    if subject_id is not None:
        query = query.filter(Task.subject_id == subject_id)

    # Nếu có chọn trạng thái -> lọc đúng trạng thái đó (TODO, IN_PROGRESS, DONE)
    effective_status = status or task_status
    if effective_status is not None:
        query = query.filter(Task.status == effective_status)

    return query.all()


# 2. API Tạo bài tập mới (POST /tasks/)
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

    # Bước 3: Lưu vào Database và làm mới dữ liệu trả về
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# 3. API Cập nhật thông tin bài tập (PUT /tasks/{task_id})
@router.put("/{task_id}", response_model=TaskResponse, summary="Cập nhật thông tin bài tập")
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập theo ID và kiểm tra quyền sở hữu thông qua bảng Subject
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

    # Bước 2: Nếu người dùng muốn đổi sang môn học khác, kiểm tra môn học mới có thuộc user không
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

    # Bước 3: Cập nhật các trường được truyền lên (bỏ qua giá trị chưa gửi)
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "subject_id":
            setattr(task, field, value)

    # Bước 4: Lưu thay đổi vào Database
    db.commit()
    db.refresh(task)
    return task


# 4. API Cập nhật nhanh trạng thái bài tập (PATCH /tasks/{task_id}/status)
@router.patch("/{task_id}/status", response_model=TaskResponse, summary="Cập nhật trạng thái bài tập")
def update_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập trong Database và đảm bảo thuộc về user đang đăng nhập
    task = (
        db.query(Task)
        .join(Subject)
        .filter(Task.id == task_id, Subject.user_id == current_user.id)
        .first()
    )

    # Bước 2: Nếu không tìm thấy hoặc không phải của user -> Báo lỗi 404
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền cập nhật!"
        )

    # Bước 3: Cập nhật trạng thái mới và lưu vào Database
    task.status = status_in.status
    db.commit()
    db.refresh(task)
    return task


# 5. API Xóa bài tập (DELETE /tasks/{task_id})
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa bài tập")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Bước 1: Tìm bài tập theo ID và đảm bảo bài tập đó thuộc về user đang đăng nhập
    task = (
        db.query(Task)
        .join(Subject)
        .filter(Task.id == task_id, Subject.user_id == current_user.id)
        .first()
    )

    # Bước 2: Nếu không tìm thấy hoặc bài tập của người khác -> Báo lỗi 404 Not Found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập hoặc bạn không có quyền xóa!"
        )

    # Bước 3: Tiến hành xóa bài tập khỏi Database và lưu lại
    db.delete(task)
    db.commit()

    # Bước 4: Trả về None với status code 204 (đúng chuẩn RESTful API khi xóa thành công)
    return None