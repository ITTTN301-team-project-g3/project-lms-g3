from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectResponse

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)

# 1. API Tạo môn học mới
@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(subject_in: SubjectCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem mã môn học đã tồn tại chưa
    existing_subject = db.query(Subject).filter(Subject.code == subject_in.code).first()
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã môn học này đã tồn tại!"
        )
    
    new_subject = Subject(
        name=subject_in.name,
        code=subject_in.code,
        description=subject_in.description,
        user_id=1  # Gán mặc định hoặc lấy từ user đang đăng nhập sau
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

# 2. API Lấy danh sách môn học
@router.get("/", response_model=List[SubjectResponse])
def get_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects