from pydantic import BaseModel
from typing import Optional
from app.schemas.subject import SubjectResponse

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject_id: int

class TaskResponse(TaskBase):
    id: int
    subject: SubjectResponse

    class Config:
        from_attributes = True