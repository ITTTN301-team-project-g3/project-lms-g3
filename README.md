# StudentHub — Hệ thống Quản lý Học tập & Bài tập Cá nhân (Project LMS)

**StudentHub** là ứng dụng web hỗ trợ sinh viên quản lý môn học, theo dõi tiến độ bài tập, tự động cảnh báo hạn nộp trực quan và thống kê hiệu suất học tập theo thời gian thực.

## Tính năng chính

1. **Đăng ký & Xác thực người dùng (JWT Authentication):**
   * Đăng ký tài khoản mới với kiểm tra định dạng email và mã hóa mật khẩu an toàn (`bcrypt`).
   * Đăng nhập cấp phát **JWT Bearer Token**; phân tách dữ liệu chặt chẽ (*Data Isolation*) giúp mỗi sinh viên chỉ xem và thao tác trên dữ liệu của riêng mình.

2. **Quản lý Môn học (Subjects CRUD):**
   * Thêm mới, xem danh sách, chỉnh sửa và xóa môn học theo mã môn và tên học phần.

3. **Quản lý Bài tập & Tiến độ (Tasks CRUD & Filter):**
   * Thêm, sửa, xóa bài tập gắn với từng môn học; hỗ trợ đặt hạn chót (`due_date`) và mô tả chi tiết.
   * Chuyển đổi nhanh trạng thái trực tiếp trên bảng (`TODO` → `IN_PROGRESS` → `DONE`).
   * Tìm kiếm bài tập theo từ khóa tiêu đề (không phân biệt hoa/thường) và lọc đa điều kiện theo môn học, trạng thái.

4. **Cảnh báo hạn nộp thông minh & Highlight UI:**
   * **Quá hạn (`is_overdue`):** Tự động gắn nhãn đỏ và tô viền cảnh báo đỏ đối với bài tập có hạn nộp nhỏ hơn thời điểm hiện tại và chưa hoàn thành.
   * **Sắp đến hạn (`is_due_soon`):** Tự động gắn nhãn vàng/cam cho bài tập có hạn nộp trong vòng **3 ngày tới**.
   * **Hoàn thành (`DONE`):** Tự động tắt toàn bộ cảnh báo trễ hạn và chuyển sang trạng thái xanh lá khi bài tập hoàn tất.

5. **Dashboard Thống kê Tổng quan:**
   * Hiển thị trực quan tổng số môn học, tổng số bài tập, số lượng bài theo từng trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) và tỷ lệ phần trăm hoàn thành (`completion_rate`).

6. **Tối ưu hiệu năng & Tài liệu API tự động:**
   * Tích hợp sẵn Index tối ưu truy vấn MySQL và middleware đo thời gian phản hồi (`X-Process-Time`), đáp ứng yêu cầu **NFR-07 (< 2 giây)**.
   * Tài liệu API tương tác chuẩn OpenAPI qua **Swagger UI** (`/docs`) và **ReDoc** (`/redoc`).

## Công nghệ sử dụng

* **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2
* **Database:** MySQL 8.0+ (hỗ trợ SQLite in-memory cho kiểm thử tự động)
* **Bảo mật:** OAuth2 Password Flow, PyJWT (`python-jose`), Passlib (`bcrypt`)
* **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript (Fetch API)
* **Kiểm thử (Testing):** Pytest, FastAPI `TestClient`

## Cấu trúc thư mục dự án

```text
project-lms-g3/
├── app/
│   ├── core/
│   │   ├── dependencies.py       # Xác thực JWT Token & lấy thông tin user hiện tại
│   │   ├── task_due_soon.py      # Logic kiểm tra bài tập sắp đến hạn (<= 3 ngày)
│   │   └── task_overdue.py       # Logic kiểm tra bài tập quá hạn
│   ├── db/
│   │   └── database.py           # Cấu hình kết nối MySQL & SQLAlchemy Session
│   ├── models/
│   │   ├── subject.py            # Model bảng subjects
│   │   ├── task.py               # Model bảng tasks & StatusEnum
│   │   └── user.py               # Model bảng users
│   ├── routers/
│   │   ├── auth.py               # API Đăng ký & Đăng nhập (/auth)
│   │   ├── dashboard.py          # API Thống kê tổng quan (/dashboard/stats)
│   │   ├── subject.py            # API Quản lý môn học (/subjects)
│   │   └── task.py               # API Quản lý bài tập & cảnh báo (/tasks)
│   └── schemas/
│       ├── subject.py            # Pydantic Schema cho Môn học
│       ├── task.py               # Pydantic Schema cho Bài tập
│       └── user.py               # Pydantic Schema cho Người dùng
├── static/
│   ├── css/
│   │   └── style.css             # Định dạng giao diện & Highlight UI cảnh báo
│   ├── js/
│   │   ├── dashboard.js          # Xử lý dữ liệu trang Dashboard
│   │   ├── subjects.js           # Xử lý CRUD trang Môn học
│   │   └── tasks.js              # Xử lý CRUD, lọc & cảnh báo trang Bài tập
│   ├── dashboard.html            # Giao diện Thống kê tổng quan
│   ├── login.html                # Giao diện Đăng nhập
│   ├── register.html             # Giao diện Đăng ký tài khoản
│   ├── subjects.html             # Giao diện Quản lý Môn học
│   └── tasks.html                # Giao diện Quản lý Bài tập
├── tests/
│   ├── test_deadline_warnings.py     # Kiểm thử logic cảnh báo hạn nộp (STT 52)
│   ├── test_integration_ac01_ac10.py # Kiểm thử tích hợp toàn hệ thống AC-01..AC-10 (STT 53)
│   ├── test_performance_nfr07.py     # Kiểm thử hiệu năng NFR-07 < 2 giây (STT 54)
│   ├── test_subjects.py              # Kiểm thử module Môn học
│   └── test_tasks.py                 # Kiểm thử module Bài tập
├── main.py                       # Điểm khởi chạy ứng dụng FastAPI, Index DB & Static Files
├── requirements.txt              # Danh sách thư viện Python phụ thuộc
└── README.md                     # Tài liệu hướng dẫn cài đặt và sử dụng
```

## Yêu cầu hệ thống

Trước khi cài đặt, hãy đảm bảo máy tính đã có sẵn:

* **Python** phiên bản `3.10` trở lên
* **MySQL Server** phiên bản `8.0` trở lên (hoặc XAMPP / Laragon / Docker MySQL)
* **Git**

## Hướng dẫn cài đặt

### Bước 1: Clone mã nguồn từ GitHub

```bash
git clone https://github.com/ITTTN301-team-project-g3/project-lms-g3.git
cd project-lms-g3
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Virtual Environment)

* **Trên Windows (Command Prompt / PowerShell):**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

* **Trên macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Bước 3: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

*(Trường hợp chưa có file `requirements.txt`, có thể cài trực tiếp bộ thư viện chuẩn bằng lệnh sau)*:

```bash
pip install fastapi uvicorn sqlalchemy pymysql "pydantic[email]" "passlib[bcrypt]" "python-jose[cryptography]" python-multipart pytest httpx
```

### Bước 4: Cấu hình Cơ sở dữ liệu MySQL

1. Khởi động dịch vụ **MySQL Server** trên máy.
2. Mở MySQL Workbench, phpMyAdmin hoặc terminal MySQL và tạo database mới:
   ```sql
   CREATE DATABASE studenthub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Kiểm tra chuỗi kết nối trong file `app/db/database.py` (hoặc file `.env` nếu dự án đang dùng biến môi trường) và cập nhật đúng `username`, `password`, `host`, `port` và tên database của bạn:
   ```python
   SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/studenthub_db"
   ```

> **Lưu ý:** Khi khởi chạy ứng dụng lần đầu, `main.py` sẽ tự động tạo toàn bộ các bảng (`users`, `subjects`, `tasks`) cùng các Index tối ưu hiệu năng (`idx_subjects_user_id`, `idx_tasks_subject_status`, `idx_tasks_due_date`).

## Hướng dẫn chạy ứng dụng

1. Tại thư mục gốc của dự án (đã kích hoạt `venv`), chạy lệnh khởi động server **Uvicorn**:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Mở trình duyệt và truy cập các đường dẫn sau:

| Chức năng / Trang | Đường dẫn URL |
| :--- | :--- |
| **Kiểm tra trạng thái Server** | `http://127.0.0.1:8000/` |
| **Trang Đăng ký tài khoản** | `http://127.0.0.1:8000/static/register.html` |
| **Trang Đăng nhập** | `http://127.0.0.1:8000/static/login.html` |
| **Trang Dashboard Thống kê** | `http://127.0.0.1:8000/static/dashboard.html` |
| **Trang Quản lý Môn học** | `http://127.0.0.1:8000/static/subjects.html` |
| **Trang Quản lý Bài tập** | `http://127.0.0.1:8000/static/tasks.html` |
| **Tài liệu API (Swagger UI)** | `http://127.0.0.1:8000/docs` |
| **Tài liệu API (ReDoc)** | `http://127.0.0.1:8000/redoc` |

## Hướng dẫn chạy kiểm thử tự động (Pytest)

Dự án sử dụng **SQLite in-memory** độc lập khi chạy test nên không làm ảnh hưởng đến dữ liệu thật trong MySQL.

* **Chạy toàn bộ bộ kiểm thử của dự án:**
  ```bash
  pytest -v
  ```

* **Chạy riêng từng bộ kiểm thử chuyên biệt:**
  ```bash
  # 1. Kiểm thử logic cảnh báo quá hạn & sắp đến hạn (STT 52)
  pytest tests/test_deadline_warnings.py -v

  # 2. Kiểm thử tích hợp toàn bộ hệ thống từ AC-01 đến AC-10 (STT 53)
  pytest tests/test_integration_ac01_ac10.py -v

  # 3. Kiểm thử đo tốc độ phản hồi hiệu năng NFR-07 < 2 giây (STT 54)
  pytest tests/test_performance_nfr07.py -v -s
  ```

## Danh sách API chính

| Nhóm | Phương thức | Endpoint | Mô tả | Yêu cầu Token |
| :--- | :---: | :--- | :--- | :---: |
| **Auth** | `POST` | `/auth/register` | Đăng ký tài khoản sinh viên mới | Không |
| **Auth** | `POST` | `/auth/login` | Đăng nhập và nhận JWT Access Token | Không |
| **Subjects** | `GET` | `/subjects/` | Lấy danh sách môn học của người dùng | Có |
| **Subjects** | `POST` | `/subjects/` | Tạo môn học mới | Có |
| **Subjects** | `PUT` | `/subjects/{subject_id}` | Cập nhật thông tin môn học | Có |
| **Subjects** | `DELETE` | `/subjects/{subject_id}` | Xóa môn học | Có |
| **Tasks** | `GET` | `/tasks/` | Xem, tìm kiếm (`search`) và lọc (`status`, `subject_id`) bài tập | Có |
| **Tasks** | `POST` | `/tasks/` | Thêm bài tập mới kèm hạn nộp | Có |
| **Tasks** | `PUT` | `/tasks/{task_id}` | Cập nhật toàn bộ thông tin bài tập | Có |
| **Tasks** | `PATCH` | `/tasks/{task_id}/status` | Đổi nhanh trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) | Có |
| **Tasks** | `DELETE` | `/tasks/{task_id}` | Xóa bài tập | Có |
| **Dashboard** | `GET` | `/dashboard/stats` | Lấy số liệu thống kê tổng quan và tỷ lệ hoàn thành | Có |

## Nhóm phát triển

* **Dự án:** Hệ thống Quản lý Học tập & Bài tập Nhóm (StudentHub / Project LMS - Nhóm G3)
* **Repository:** [ITTTN301-team-project-g3/project-lms-g3](https://github.com/ITTTN301-team-project-g3/project-lms-g3)