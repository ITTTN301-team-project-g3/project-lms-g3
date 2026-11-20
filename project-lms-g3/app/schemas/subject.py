from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SubjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Tên môn học")
    code: str = Field(..., min_length=2, max_length=50, description="Mã môn học")
    description: Optional[str] = Field(None, description="Mô tả chi tiết môn học")

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

class SubjectResponse(SubjectBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)