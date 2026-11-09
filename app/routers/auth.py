from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token

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

@router.post("/login", summary="Đăng nhập hệ thống (Lấy Token)")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Tìm user qua email (OAuth2 mặc định gửi email vào biến username)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Tạo Access Token (Ép ID về kiểu chuỗi "sub" để khớp với file dependencies.py của cậu)
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }