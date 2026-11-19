from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.models.task import StatusEnum
from app.core.task_overdue import is_task_overdue
from app.core.task_due_soon import is_task_due_soon

TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Tiêu đề bài tập")
    description: Optional[str] = Field(None, description="Mô tả chi tiết yêu cầu bài tập")
    due_date: Optional[datetime] = Field(
        None, description="Hạn nộp bài (ISO 8601, VD: 2026-11-20T23:59:00)"
    )
    status: TaskStatus = Field(default="TODO", description="Trạng thái: TODO, IN_PROGRESS, DONE")


class TaskCreate(TaskBase):
    subject_id: int = Field(..., gt=0, description="ID của môn học chứa bài tập này")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    subject_id: Optional[int] = Field(None, gt=0)


class TaskResponse(TaskBase):
    id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return is_task_overdue(self.due_date, self.status)

    @computed_field
    @property
    def is_due_soon(self) -> bool:
        return is_task_due_soon(self.due_date, self.status)


class TaskStatusUpdate(BaseModel):
    status: StatusEnum = Field(..., description="Trạng thái mới của bài tập")