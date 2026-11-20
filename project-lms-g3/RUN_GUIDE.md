# HUONG DAN CAI DAT VA CHAY LMS

## 1. Yeu cau
- Python 3.10 tro len (khuyen nghi Python 3.12).
- MySQL 8.
- VS Code hoac Terminal.

## 2. Tao database
Trong MySQL Workbench chay:

```sql
CREATE DATABASE IF NOT EXISTS team_project_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

## 3. Cau hinh moi truong
1. Copy `.env.example` thanh `.env`.
2. Mo `.env` va dien dung thong tin MySQL cua may.

Vi du:

```env
DATABASE_URL=mysql+pymysql://root:MAT_KHAU_MYSQL@localhost:3306/team_project_db
SECRET_KEY=thay_bang_mot_chuoi_bi_mat_dai_va_ngau_nhien
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

Khong commit hoac chia se file `.env` co mat khau that.

## 4. Cai dat va chay tren Windows PowerShell

Mo Terminal tai thu muc goc `project-lms-g3`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Neu PowerShell chan script kich hoat:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 5. Cap nhat database cu
`Base.metadata.create_all()` tao cac bang con thieu nhung khong tu them cot vao bang da ton tai.

Neu database cu da co bang `tasks` voi `id`, `title`, `description`, `subject_id`, `user_id` nhung chua co `due_date`, `status`, chay mot lan:

```sql
ALTER TABLE team_project_db.tasks
ADD COLUMN due_date DATETIME NULL,
ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'TODO';
```

Neu hai cot da ton tai thi bo qua lenh ALTER nay.

## 6. Tao du lieu demo

Sau khi `.env` va ket noi MySQL da dung:

```powershell
python seed_data.py
```

Tai khoan demo va mat khau duoc liet ke trong `DEMO_GUIDE.md`.

## 7. Chay ung dung

```powershell
uvicorn main:app --reload
```

Mo cac dia chi:
- Trang dang nhap: http://127.0.0.1:8000/static/login.html
- Trang dang ky: http://127.0.0.1:8000/static/register.html
- Dashboard: http://127.0.0.1:8000/static/dashboard.html
- Swagger API: http://127.0.0.1:8000/docs

## 8. Chay test

```powershell
pytest -q
```

Luu y: cac test hien co ket noi toi database duoc cau hinh trong `.env`; nen dung database test rieng neu muon chay test ma khong them tai khoan vao database demo.
