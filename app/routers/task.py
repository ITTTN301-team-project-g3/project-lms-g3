from datetime import datetime, time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

# Import kết nối database và các models/schemas liên quan
from app.db.database import get_db
from app.models.task import Task
from app.models.subject import Subject
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from app.core.dependencies import get_current_user

# Import 2 hàm kiểm tra quá hạn và sắp đến hạn từ module core của nhóm
from app.core.task_overdue import is_task_overdue
from app.core.task_due_soon import is_task_due_soon

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={
        401: {"description": "Chưa xác thực hoặc JWT Bearer Token không hợp lệ/hết hạn."},
    },
)


# Schema nhận dữ liệu trạng thái mới khi gọi API PATCH
class TaskStatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"status": "IN_PROGRESS"},
                {"status": "DONE"},
            ]
        }
    )

    status: TaskStatus = Field(
        ...,
        description="Trạng thái mới của bài tập: `TODO`, `IN_PROGRESS`, hoặc `DONE`.",
    )


# Hàm hỗ trợ tính toán và gắn cờ quá hạn / sắp đến hạn cho từng bài tập
def attach_deadline_flags(task: Task) -> Task:
    status_str = task.status.value if hasattr(task.status, "value") else str(task.status)
    due_dt = task.due_date

    # Chuyển đổi sang datetime nếu cột due_date trong model đang lưu kiểu date
    if due_dt is not None and not isinstance(due_dt, datetime):
        due_dt = datetime.combine(due_dt, time(23, 59, 59))

    task.is_overdue = is_task_overdue(due_dt, status_str)
    task.is_due_soon = is_task_due_soon(due_dt, status_str)
    return task


# 1. API Xem, Tìm kiếm và Lọc danh sách bài tập (GET /tasks/)
@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Xem, tìm kiếm và lọc danh sách bài tập",
    description=(
        "Lấy danh sách bài tập thuộc các môn học của người dùng hiện tại.\n\n"
        "- **Tìm kiếm (`search`):** Tìm gần đúng (không phân biệt hoa/thường) theo tiêu đề bài tập.\n"
        "- **Lọc theo môn học (`subject_id`):** Chỉ lấy bài tập của môn học có ID tương ứng.\n"
        "- **Lọc theo trạng thái (`status` / `task_status`):** Lọc theo `TODO`, `IN_PROGRESS` hoặc `DONE`.\n"
        "- **Trường tính toán tự động:** Mỗi phần tử trả về kèm `is_overdue` (quá hạn & chưa `DONE`) "
        "và `is_due_soon` (hạn trong 3 ngày tới & chưa `DONE`)."
    ),
)
def get_tasks(
    search: Optional[str] = Query(
        default=None,
        description="Từ khóa tìm kiếm theo tiêu đề bài tập (không phân biệt hoa/thường).",
        examples=["báo cáo"],
    ),
    status: Optional[TaskStatus] = Query(
        default=None,
        description="Lọc theo trạng thái bài tập (`TODO`, `IN_PROGRESS`, `DONE`).",
    ),
    task_status: Optional[TaskStatus] = Query(
        default=None,
        description="Tham số thay thế cho `status` để lọc theo trạng thái bài tập (`TODO`, `IN_PROGRESS`, `DONE`).",
    ),
    subject_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="ID môn học cần lọc bài tập.",
        examples=[1],
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    tasks = query.all()

    # Gắn thêm thông tin cảnh báo quá hạn / sắp đến hạn trước khi trả về Frontend
    for task in tasks:
        attach_deadline_flags(task)

    return tasks


# 2. API Tạo bài tập mới (POST /tasks/)
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm bài tập mới",
    description=(
        "Tạo một bài tập mới gắn với `subject_id` thuộc sở hữu của tài khoản đang đăng nhập.\n\n"
        "- Trả về **201 Created** kèm thông tin bài tập vừa tạo và các cờ `is_overdue`, `is_due_soon`.\n"
        "- Trả về **404 Not Found** nếu `subject_id` không tồn tại hoặc không thuộc người dùng hiện tại."
    ),
    responses={
        404: {"description": "Không tìm thấy môn học hoặc môn học không thuộc quyền sở hữu của người dùng."},
    },
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Bước 1: Kiểm tra môn học có tồn tại và thuộc sở hữu của user đang đăng nhập không
    subject = db.query(Subject).filter(
        Subject.id == task_in.subject_id,
        Subject.user_id == current_user.id,
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học hoặc bạn không có quyền thêm bài tập vào môn học này!",
        )

    # Bước 2: Khởi tạo đối tượng bài tập mới
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        subject_id=task_in.subject_id,
    )

    # Bước 3: Lưu vào Database và làm mới dữ liệu trả về
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return attach_deadline_flags(new_task)


# 3. API Cập nhật thông tin bài tập (PUT /tasks/{task_id})
@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Cập nhật thông tin bài tập",
    description=(
        "Cập nhật các thông tin của bài tập theo `task_id` (tiêu đề, mô tả, hạn nộp, trạng thái hoặc chuyển sang `subject_id` khác).\n\n"
        "- Chỉ cập nhật các trường được gửi lên (bỏ qua trường không truyền).\n"
        "- Kiểm tra quyền sở hữu bài tập và môn học đích (nếu có đổi `subject_id`)."
    ),
    responses={
        404: {"description": "Không tìm thấy bài tập hoặc môn học đích, hoặc người dùng không có quyền thao tác."},
    },
)
def update_task(
    task_id: int = Path(..., gt=0, description="ID của bài tập cần cập nhật.", examples=[1]),
    task_in: TaskUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Không tìm thấy bài tập hoặc bạn không có quyền chỉnh sửa bài tập này!",
        )

    # Bước 2: Nếu người dùng muốn đổi sang môn học khác, kiểm tra môn học mới có thuộc user không
    if task_in.subject_id is not None:
        subject = db.query(Subject).filter(
            Subject.id == task_in.subject_id,
            Subject.user_id == current_user.id,
        ).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy môn học mới hoặc bạn không sở hữu môn học này!",
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
    return attach_deadline_flags(task)


# 4. API Cập nhật nhanh trạng thái bài tập (PATCH /tasks/{task_id}/status)
@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Cập nhật trạng thái bài tập",
    description=(
        "Cập nhật nhanh trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) cho bài tập theo `task_id`.\n\n"
        "Khi chuyển trạng thái sang `DONE`, `is_overdue` và `is_due_soon` trong phản hồi sẽ tự động chuyển về `false`."
    ),
    responses={
        404: {"description": "Không tìm thấy bài tập hoặc bài tập không thuộc quyền sở hữu của người dùng."},
    },
)
def update_task_status(
    task_id: int = Path(..., gt=0, description="ID của bài tập cần cập nhật trạng thái.", examples=[1]),
    status_in: TaskStatusUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Không tìm thấy bài tập hoặc bạn không có quyền cập nhật!",
        )

    # Bước 3: Cập nhật trạng thái mới và lưu vào Database
    task.status = status_in.status
    db.commit()
    db.refresh(task)
    return attach_deadline_flags(task)


# 5. API Xóa bài tập (DELETE /tasks/{task_id})
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bài tập",
    description=(
        "Xóa vĩnh viễn bài tập theo `task_id` nếu bài tập thuộc môn học của người dùng hiện tại.\n\n"
        "Trả về **204 No Content** khi xóa thành công (không có nội dung body)."
    ),
    responses={
        404: {"description": "Không tìm thấy bài tập hoặc người dùng không có quyền xóa."},
    },
)
def delete_task(
    task_id: int = Path(..., gt=0, description="ID của bài tập cần xóa.", examples=[1]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail="Không tìm thấy bài tập hoặc bạn không có quyền xóa!",
        )

    # Bước 3: Tiến hành xóa bài tập khỏi Database và lưu lại
    db.delete(task)
    db.commit()

    # Bước 4: Trả về None với status code 204 (đúng chuẩn RESTful API khi xóa thành công)
    return None