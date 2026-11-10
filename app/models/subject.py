from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Khóa ngoại liên kết với bảng users
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Quan hệ ngược lại với Model User (nếu cần truy xuất user.subjects)
    creator = relationship("User", back_populates="subjects")