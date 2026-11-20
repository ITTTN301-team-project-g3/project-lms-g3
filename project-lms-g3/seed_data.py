from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task
from app.core.security import get_password_hash


DEMO_PASSWORD = "Demo@123456"

DEMO_USERS = [
    {"full_name": "Nguyen Van An", "email": "demo1@lms.com"},
    {"full_name": "Tran Thi Binh", "email": "demo2@lms.com"},
    {"full_name": "Le Minh Khoa", "email": "demo3@lms.com"},
]

SUBJECTS = [
    ("CS101", "Lap trinh co ban", "Bien, kieu du lieu, cau truc dieu khien, ham va mang."),
    ("CS102", "Cau truc du lieu va giai thuat", "Stack, Queue, Linked List, sap xep va tim kiem."),
    ("DB201", "Co so du lieu", "Mo hinh ERD, SQL, khoa va cac phep JOIN."),
    ("WEB201", "Lap trinh Web", "HTML, CSS, JavaScript va xay dung giao dien."),
    ("SE202", "Cong nghe phan mem", "Phan tich yeu cau, SRS, UML va quy trinh phat trien."),
    ("NET201", "Mang may tinh", "Mo hinh OSI, TCP/IP, dia chi IP va cac giao thuc."),
    ("PY101", "Lap trinh Python", "Cu phap Python, ham, OOP va xu ly tep."),
    ("ENG101", "Tieng Anh chuyen nganh", "Tu vung va doc hieu tai lieu cong nghe thong tin."),
]

# (title, description, so ngay so voi hom nay, status)
TASK_TEMPLATES = {
    "CS101": [
        ("On tap chuong 1", "Doc lai ly thuyet va ghi chu cac khai niem quan trong.", -5, "DONE"),
        ("Bai tap thuc hanh", "Hoan thanh bai tap tren lop va nop ma nguon.", 0, "IN_PROGRESS"),
        ("Bai tap ve nha", "Lam bai tap cuoi chuong va viet giai thich.", 3, "TODO"),
        ("Mini project", "Xay dung chuong trinh nho ap dung kien thuc da hoc.", 8, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "CS102": [
        ("Tom tat kien thuc", "Tong hop Stack, Queue, Linked List va do phuc tap.", -2, "DONE"),
        ("Cai dat thuat toan", "Viet code va kiem tra cac truong hop bien.", 2, "IN_PROGRESS"),
        ("Phan tich do phuc tap", "Phan tich time complexity va space complexity.", 6, "TODO"),
        ("Kiem tra thuc hanh", "Hoan thanh bai kiem tra va nop tep bai lam.", 12, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "DB201": [
        ("Ve mo hinh ERD", "Xac dinh thuc the, thuoc tinh va moi quan he.", -4, "DONE"),
        ("Tao co so du lieu", "Tao bang, khoa chinh, khoa ngoai va rang buoc.", 1, "IN_PROGRESS"),
        ("Truy van SQL", "Viet SELECT, JOIN, GROUP BY va truy van con.", 5, "TODO"),
        ("Bao cao Database", "Chup anh ket qua va viet bao cao thuc hanh.", 10, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "WEB201": [
        ("Hoan thanh giao dien HTML", "Dung HTML tao bo cuc trang web co ban.", -3, "DONE"),
        ("Thuc hanh CSS", "Dinh dang bo cuc, mau sac va responsive.", 2, "IN_PROGRESS"),
        ("Bai tap JavaScript", "Xu ly su kien, form va kiem tra du lieu.", 7, "TODO"),
        ("Hoan thien trang web", "Ket hop HTML, CSS, JavaScript va kiem tra.", 14, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "SE202": [
        ("Doc tai lieu SRS", "Xac dinh muc tieu, pham vi va doi tuong su dung.", -1, "DONE"),
        ("Ve Use Case Diagram", "Xac dinh actor va cac chuc nang he thong.", 3, "IN_PROGRESS"),
        ("Thiet ke co so du lieu", "Mo ta cac bang va moi quan he trong he thong.", 8, "TODO"),
        ("Viet bao cao du an", "Tong hop phan tich va thiet ke he thong.", 15, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "NET201": [
        ("On tap mo hinh OSI", "Mo ta chuc nang cua 7 tang trong mo hinh OSI.", -6, "DONE"),
        ("Bai tap dia chi IP", "Lam bai tap chia subnet va xac dinh network.", 2, "IN_PROGRESS"),
        ("Cau hinh mang", "Cau hinh IP va kiem tra ket noi giua cac may.", 9, "TODO"),
        ("Bao cao giao thuc mang", "Trinh bay TCP, UDP, DNS va HTTP.", 16, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "PY101": [
        ("On tap cu phap Python", "On tap bien, vong lap, ham va danh sach.", -2, "DONE"),
        ("Xu ly danh sach", "Viet chuong trinh them, sua, xoa va tim kiem.", 1, "IN_PROGRESS"),
        ("Lap trinh huong doi tuong", "Tao class, object, constructor va method.", 6, "TODO"),
        ("Bai tap cuoi mon", "Xay dung ung dung nho bang Python.", 13, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
    "ENG101": [
        ("Hoc tu vung IT", "Hoc va dat cau voi 20 tu vung cong nghe thong tin.", -1, "DONE"),
        ("Doc bai bao cong nghe", "Doc tai lieu tieng Anh va ghi lai y chinh.", 4, "IN_PROGRESS"),
        ("Viet doan gioi thieu", "Gioi thieu mot san pham cong nghe bang tieng Anh.", 9, "TODO"),
        ("Thuyet trinh chu de IT", "Chuan bi noi dung va slide thuyet trinh bang tieng Anh.", 17, "TODO"),
        ("Bai tap can xu ly bo sung", "Bai tap mau qua han de minh hoa canh bao tren Dashboard.", -2, "TODO"),
    ],
}


def get_or_create_user(db: Session, user_data: dict) -> User:
    user = db.query(User).filter(User.email == user_data["email"]).first()
    if user:
        print(f"[EXISTS] {user.email}")
        return user

    user = User(
        full_name=user_data["full_name"],
        email=user_data["email"],
        password_hash=get_password_hash(DEMO_PASSWORD),
        is_active=True,
        role="USER",
    )
    db.add(user)
    db.flush()
    print(f"[CREATED USER] {user.email}")
    return user


def seed_user_data(db: Session, user: User):
    new_subjects = 0
    new_tasks = 0

    for code, name, description in SUBJECTS:
        subject = db.query(Subject).filter(
            Subject.user_id == user.id,
            Subject.code == code
        ).first()

        if subject is None:
            subject = Subject(
                code=code,
                name=name,
                description=description,
                user_id=user.id,
            )
            db.add(subject)
            db.flush()
            new_subjects += 1
            print(f"  [CREATED SUBJECT] {code} - {name}")

        for title, task_description, day_offset, task_status in TASK_TEMPLATES[code]:
            existing_task = db.query(Task).filter(
                Task.user_id == user.id,
                Task.subject_id == subject.id,
                Task.title == title,
            ).first()

            if existing_task:
                continue

            due_date = (
                datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
                + timedelta(days=day_offset)
            )

            task = Task(
                title=title,
                description=task_description,
                due_date=due_date,
                status=task_status,
                subject_id=subject.id,
                user_id=user.id,
            )
            db.add(task)
            new_tasks += 1
            print(f"    [CREATED TASK] {title}")

    return new_subjects, new_tasks


def main():
    # Tao cac bang con thieu theo Model; khong xoa hoac ghi de bang hien co.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_subjects = 0
    total_tasks = 0

    try:
        for user_data in DEMO_USERS:
            user = get_or_create_user(db, user_data)
            subjects, tasks = seed_user_data(db, user)
            total_subjects += subjects
            total_tasks += tasks

        db.commit()

        print("\\n========== SEED DATA COMPLETED ==========")
        print(f"Demo accounts checked: {len(DEMO_USERS)}")
        print(f"New subjects created: {total_subjects}")
        print(f"New tasks created: {total_tasks}")
        print(f"Demo password: {DEMO_PASSWORD}")
        print("Existing records were kept; running this script again will not duplicate seed records.")

    except Exception as error:
        db.rollback()
        print(f"\\n[ERROR] Seed data failed: {error}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
