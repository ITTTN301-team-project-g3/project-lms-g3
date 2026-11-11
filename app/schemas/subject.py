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

# 5. Schema cơ bản chứa các trường dữ liệu chung của Môn học
class SubjectBase(BaseModel):
    name: str          # Tên môn học (bắt buộc nhập)
    code: str          # Mã môn học (bắt buộc nhập, ví dụ: INT1234)
    description: Optional[str] = None  # Mô tả môn học (có thể để trống, mặc định là None)

# 6. Schema nhận dữ liệu khi gửi Request tạo môn học mới (POST /subjects/)
class SubjectCreate(SubjectBase):
    pass  # Kế thừa toàn bộ các trường từ SubjectBase (name, code, description)

# 7. Schema định dạng dữ liệu trả về cho Client (Response Body)
class SubjectResponse(SubjectBase):
    id: int       # ID tự tăng của môn học trong Database
    user_id: int  # ID của người dùng sở hữu môn học này

    # Cấu hình Pydantic v2 cho phép chuyển đổi tự động từ đối tượng SQLAlchemy Model sang Pydantic Schema
    model_config = ConfigDict(from_attributes=True)