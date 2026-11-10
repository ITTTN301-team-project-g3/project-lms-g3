from pydantic import BaseModel
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True