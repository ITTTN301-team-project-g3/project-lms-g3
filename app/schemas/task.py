from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import StatusEnum

# Định nghĩa các trạng thái hợp lệ của bài tập
TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE"]

# 1. Base Schema - Chứa các trường dữ liệu chung của Bài tập
class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Tiêu đề bài tập")
    description: Optional[str] = Field(None, description="Mô tả chi tiết yêu cầu bài tập")
    due_date: Optional[datetime] = Field(None, description="Hạn nộp bài (ISO 8601, VD: 2026-11-20T23:59:00)")
    status: TaskStatus = Field(default="TODO", description="Trạng thái: TODO, IN_PROGRESS, DONE")

# 2. Schema dùng khi Client gửi request TẠO bài tập mới (POST /tasks/)
class TaskCreate(TaskBase):
    subject_id: int = Field(..., gt=0, description="ID của môn học chứa bài tập này")

# 3. Schema dùng khi Client gửi request CẬP NHẬT bài tập (PUT /tasks/{task_id})
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    subject_id: Optional[int] = Field(None, gt=0)

# 4. Schema định dạng dữ liệu trả về cho Client (Response Body)
class TaskResponse(TaskBase):
    id: int
    subject_id: int

    is_overdue: bool = False
    is_due_soon: bool = False
    model_config = ConfigDict(from_attributes=True)
# 5. Schema định nghĩa trạng thái bài tập
class TaskStatusUpdate(BaseModel):
    status: StatusEnum = Field(..., description="Trạng thái mới của bài tập")