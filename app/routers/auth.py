from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User  # Nếu file model tên user.py
from app.schemas.user import UserCreate, UserResponse  # Pydantic Schemas
from app.core.security import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Đăng ký tài khoản mới")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra email đã tồn tại trong MySQL chưa
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng trên hệ thống!"
        )

    # 2. Mã hóa mật khẩu bằng hàm hash_password trong app/core/security.py
    hashed_pwd = hash_password(user_data.password)

    # 3. Tạo User object mới
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pwd,
        role="USER"
    )

    # 4. Lưu vào Database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user