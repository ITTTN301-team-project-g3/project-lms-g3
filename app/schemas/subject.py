from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

# 1. Base Schema - Chứa các trường chung
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Tên môn học")
    code: str = Field(..., min_length=2, max_length=50, description="Mã môn học (Ví dụ: INT1340)")
    description: Optional[str] = Field(None, description="Mô tả chi tiết môn học")

# 2. Schema dùng khi Client gửi request TẠO môn học
class SubjectCreate(SubjectBase):
    pass

# 3. Schema dùng khi Client gửi request SỬA môn học (Task 24)
class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

# 4. Schema dùng để trả dữ liệu về cho Client (Response)
class SubjectResponse(SubjectBase):
    id: int
    user_id: int

    # Chuẩn Pydantic V2 để chuyển đổi từ SQLAlchemy Model sang JSON
    model_config = ConfigDict(from_attributes=True)