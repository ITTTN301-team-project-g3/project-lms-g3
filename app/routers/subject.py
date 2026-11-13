from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import phiên làm việc DB và các Model/Schema cần thiết
from app.db.database import get_db
from app.models.subject import Subject
from app.models.task import Task # 👈 Import model Task để kiểm tra lúc xóa
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate

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

# 3. API Sửa môn học
# Đường dẫn: PUT /subjects/{subject_id}
@router.put("/{subject_id}", response_model=SubjectResponse, summary="Sửa thông tin môn học")
def update_subject(
    subject_id: int, 
    subject_in: SubjectUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm môn học theo ID và đảm bảo môn đó của user đang đăng nhập
    subject = db.query(Subject).filter(
        Subject.id == subject_id, 
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy môn học hoặc bạn không có quyền sửa!")
    
    # Nếu user muốn đổi mã môn học (code), kiểm tra xem mã mới có trùng với mã nào khác của user này không
    if subject_in.code and subject_in.code != subject.code:
        existing_code = db.query(Subject).filter(
            Subject.code == subject_in.code, 
            Subject.user_id == current_user.id
        ).first()
        if existing_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã môn học mới đã tồn tại trong tài khoản của bạn!")

    # Cập nhật các trường có gửi lên
    if subject_in.name is not None:
        subject.name = subject_in.name
    if subject_in.code is not None:
        subject.code = subject_in.code
    if subject_in.description is not None:
        subject.description = subject_in.description

    db.commit()
    db.refresh(subject)
    return subject


# 4. API Xóa môn học
# Đường dẫn: DELETE /subjects/{subject_id}
@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa môn học")
def delete_subject(
    subject_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id, 
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy môn học hoặc bạn không có quyền xóa!")
    
    # ĐOẠN NÀY LÀ ĐỂ HOÀN THÀNH TASK STT 26 ĐÓ: Kiểm tra xem môn học có bài tập nào không
    linked_tasks = db.query(Task).filter(Task.subject_id == subject_id).first()
    if linked_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa! Môn học này đang chứa bài tập."
        )
    
    db.delete(subject)
    db.commit()
    return