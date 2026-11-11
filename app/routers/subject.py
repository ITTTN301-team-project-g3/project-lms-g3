from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import phiên làm việc DB và các Model/Schema cần thiết
from app.db.database import get_db
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectResponse

# Import dependency xác thực Token người dùng
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)

# 1. API Tạo môn học mới
# Đường dẫn: POST /subjects/
# Status Code: 201 Created

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED,summary="Thêm môn học mới")
def create_subject(subject_in: SubjectCreate, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Giải mã Token để lấy thông tin User đang đăng nhập
):
    # Bước 1: Kiểm tra xem mã môn học này đã tồn tại trong tài khoản của User hiện tại chưa
    existing_subject = db.query(Subject).filter(
        Subject.code == subject_in.code,
        Subject.user_id == current_user.id
    ).first()
    
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã môn học này đã tồn tại trong tài khoản của bạn!"
        )
    
    # Bước 2: Khởi tạo đối tượng môn học mới, tự động lấy user_id từ Token
    new_subject = Subject(
        name=subject_in.name,
        code=subject_in.code,
        description=subject_in.description,
        user_id=current_user.id  # Gán ID người dùng đang đăng nhập (không dùng hardcode user_id = 1)
    )
    
    # Bước 3: Lưu vào MySQL và refresh để lấy ID vừa khởi tạo
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return new_subject

# 2. API Xem danh sách môn học
# Đường dẫn: GET /subjects/
# Status Code: 200 OK
@router.get("/", response_model=List[SubjectResponse],summary="Xem danh sách môn học")
def get_subjects(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)  # Yêu cầu phải đăng nhập mới xem được
):
    # Bước 1: Truy vấn chỉ lấy các môn học thuộc sở hữu của chính User đang đăng nhập
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    
    return subjects