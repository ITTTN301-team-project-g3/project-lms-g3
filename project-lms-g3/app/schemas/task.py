from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: TaskStatus = "TODO"


class TaskCreate(TaskBase):
    subject_id: int = Field(..., gt=0)


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
