
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import StatusEnum

# Định nghĩa các trạng thái hợp lệ của bài tập
TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE"]


# 1. Base Schema - Chứa các trường dữ liệu chung của Bài tập
class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Tiêu đề bài tập (từ 2 đến 255 ký tự).",
    )
    description: Optional[str] = Field(
        None,
        description="Mô tả chi tiết yêu cầu bài tập (không bắt buộc).",
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Hạn nộp bài theo định dạng ISO 8601 (VD: 2026-11-20T23:59:00).",
    )
    status: TaskStatus = Field(
        default="TODO",
        description="Trạng thái xử lý bài tập: `TODO`, `IN_PROGRESS`, hoặc `DONE`.",
    )


# 2. Schema dùng khi Client gửi request TẠO bài tập mới (POST /tasks/)
class TaskCreate(TaskBase):
    subject_id: int = Field(
        ...,
        gt=0,
        description="ID của môn học chứa bài tập này (phải thuộc quyền sở hữu của người dùng).",
    )


# 3. Schema dùng khi Client gửi request CẬP NHẬT bài tập (PUT /tasks/{task_id})
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Tiêu đề mới của bài tập (từ 2 đến 255 ký tự).",
    )
    description: Optional[str] = Field(
        None,
        description="Mô tả chi tiết mới của bài tập.",
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Hạn nộp bài mới theo định dạng ISO 8601.",
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Trạng thái mới của bài tập: `TODO`, `IN_PROGRESS`, hoặc `DONE`.",
    )
    subject_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID môn học mới nếu muốn chuyển bài tập sang môn khác.",
    )


# 4. Schema định dạng dữ liệu trả về cho Client (Response Body)
class TaskResponse(TaskBase):
    id: int = Field(..., description="ID duy nhất của bài tập.")
    subject_id: int = Field(..., description="ID môn học chứa bài tập.")

    is_overdue: bool = Field(
        default=False,
        description="`true` nếu bài tập đã quá hạn (`due_date < hiện tại`) và trạng thái khác `DONE`.",
    )
    is_due_soon: bool = Field(
        default=False,
        description="`true` nếu hạn nộp nằm trong vòng 3 ngày tới và trạng thái khác `DONE`.",
    )
    model_config = ConfigDict(from_attributes=True)


# 5. Schema định nghĩa trạng thái bài tập
class TaskStatusUpdate(BaseModel):
    status: StatusEnum = Field(
        ...,
        description="Trạng thái mới của bài tập (`TODO`, `IN_PROGRESS`, `DONE`).",
    )