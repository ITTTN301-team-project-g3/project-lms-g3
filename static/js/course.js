const SUBJECT_API_URL = "http://127.0.0.1:8000/subjects/";
const TASK_API_URL = "http://127.0.0.1:8000/tasks/";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/static/login.html";
}

const COURSE_CURRICULUM = {
    INT1434: [
        {
            chapter: "Chương 1: Nền tảng Web & Giao thức HTTP",
            lessons: [
                {
                    id: "w1",
                    title: "Sơ lược về Internet & Mô hình Client - Server",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Internet và World Wide Web hoạt động như thế nào?</h5>
                        <ul>
                            <li><strong>Internet</strong> là mạng lưới toàn cầu kết nối hàng tỷ thiết bị máy tính và máy chủ thông qua bộ giao thức chuẩn <strong>TCP/IP</strong>.</li>
                            <li><strong>Mô hình Client - Server:</strong> Trình duyệt web đóng vai trò là <em>Client</em> gửi yêu cầu (HTTP Request) tới <em>Server</em> (máy chủ chạy FastAPI). Server xử lý nghiệp vụ, truy vấn cơ sở dữ liệu và trả về kết quả (HTTP Response).</li>
                            <li><strong>DNS (Domain Name System):</strong> Hệ thống phân giải tên miền dễ nhớ thành địa chỉ IP vật lý của máy chủ.</li>
                        </ul>
                        <h5>II. Cấu trúc một gói tin HTTP Request & Response</h5>
                        <ul>
                            <li><strong>Request Line:</strong> Gồm phương thức (<code>GET</code>, <code>POST</code>, <code>PUT</code>, <code>PATCH</code>, <code>DELETE</code>), đường dẫn tài nguyên (ví dụ <code>/tasks/</code>) và phiên bản HTTP.</li>
                            <li><strong>Headers:</strong> Chứa siêu dữ liệu như <code>Content-Type: application/json</code> hoặc <code>Authorization: Bearer &lt;token&gt;</code>.</li>
                            <li><strong>Body:</strong> Dữ liệu JSON gửi kèm khi tạo mới hoặc cập nhật bản ghi.</li>
                        </ul>
                        <div class="lms-callout-box">
                            <strong>Ghi nhớ nhanh:</strong> Mã trạng thái <code>200 OK</code> là thành công, <code>201 Created</code> là tạo mới thành công, <code>401 Unauthorized</code> là thiếu hoặc sai Token đăng nhập, <code>422 Unprocessable Entity</code> là dữ liệu gửi lên sai định dạng.
                        </div>
                    `
                },
                {
                    id: "w2",
                    title: "Thiết kế RESTful API chuẩn công nghiệp",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Nguyên tắc cốt lõi của RESTful API</h5>
                        <ul>
                            <li><strong>Stateless (Phi trạng thái):</strong> Mỗi yêu cầu từ Client gửi lên Server phải chứa đầy đủ thông tin xác thực (JWT Token), Server không lưu phiên đăng nhập trong bộ nhớ RAM.</li>
                            <li><strong>Định danh tài nguyên bằng danh từ số nhiều:</strong> Sử dụng <code>/subjects/</code> và <code>/tasks/</code> thay vì dùng động từ như <code>/getAllTasks</code>.</li>
                        </ul>
                        <h5>II. Bảng ánh xạ hành động CRUD sang HTTP Method</h5>
                        <ul>
                            <li><code>GET /tasks/</code>: Lấy danh sách toàn bộ bài tập của người dùng hiện tại.</li>
                            <li><code>POST /tasks/</code>: Tạo một bài tập mới gắn với môn học.</li>
                            <li><code>PATCH /tasks/{id}/status</code>: Cập nhật một phần dữ liệu (chỉ đổi trạng thái bài tập).</li>
                            <li><code>DELETE /tasks/{id}</code>: Xóa bài tập và trả về mã <code>204 No Content</code>.</li>
                        </ul>
                    `
                },
                {
                    id: "w3",
                    title: "Cấu trúc dự án Web Full-Stack thực tế",
                    duration: "8 phút đọc",
                    content: `
                        <h5>I. Phân tách tầng trách nhiệm (Separation of Concerns)</h5>
                        <ul>
                            <li><strong>Tầng Models (<code>app/models/</code>):</strong> Định nghĩa cấu trúc bảng dữ liệu và quan hệ khóa ngoại.</li>
                            <li><strong>Tầng Schemas (<code>app/schemas/</code>):</strong> Kiểm tra tính hợp lệ của dữ liệu đầu vào và lọc dữ liệu trả ra bằng Pydantic.</li>
                            <li><strong>Tầng Routers (<code>app/routers/</code>):</strong> Tiếp nhận request, gọi xử lý nghiệp vụ và trả response.</li>
                            <li><strong>Tầng Frontend (<code>static/</code>):</strong> Tách biệt hoàn toàn HTML (khung giao diện), CSS (hiệu ứng thẩm mỹ) và JavaScript (gọi API và thao tác DOM).</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 2: Xây dựng Backend với FastAPI",
            lessons: [
                {
                    id: "w4",
                    title: "Khởi tạo ứng dụng FastAPI & Dependency Injection",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Tại sao chọn FastAPI?</h5>
                        <ul>
                            <li>Hiệu năng cao ngang ngửa NodeJS và Go nhờ chuẩn bất đồng bộ <strong>ASGI (Uvicorn)</strong>.</li>
                            <li>Tự động sinh trang tài liệu kiểm thử API trực quan tại <code>/docs</code> (Swagger UI).</li>
                        </ul>
                        <h5>II. Cơ chế Dependency Injection với <code>Depends()</code></h5>
                        <p>Thay vì lặp lại code mở kết nối Database hay kiểm tra đăng nhập ở mọi hàm, ta tách thành các hàm phụ thuộc dùng chung:</p>
                        <div class="lms-code-block">@router.get("/tasks/")
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Task).all()</div>
                    `
                },
                {
                    id: "w5",
                    title: "Kiểm tra dữ liệu đầu vào với Pydantic Schema",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Vai trò của Pydantic</h5>
                        <ul>
                            <li>Tự động ép kiểu dữ liệu (ví dụ chuỗi <code>"2026-11-25"</code> sang đối tượng <code>date</code> trong Python).</li>
                            <li>Ngăn chặn dữ liệu rác lọt vào Database bằng các ràng buộc độ dài, định dạng Email hoặc kiểu Enum cố định.</li>
                        </ul>
                        <div class="lms-code-block">class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date
    status: TaskStatus = TaskStatus.TODO
    subject_id: int</div>
                    `
                },
                {
                    id: "w6",
                    title: "Xử lý ngoại lệ & Mã lỗi HTTPException",
                    duration: "9 phút đọc",
                    content: `
                        <h5>I. Trả về thông báo lỗi rõ ràng cho Frontend</h5>
                        <ul>
                            <li>Khi người dùng truy cập tài nguyên không tồn tại hoặc không thuộc quyền sở hữu, Backend chủ động ném lỗi <code>HTTPException</code> thay vì để chương trình sập (lỗi 500).</li>
                            <li>Ví dụ: Trả về <code>status_code=404</code> kèm thông báo tiếng Việt giúp giao diện hiển thị cảnh báo thân thiện.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 3: Cơ sở dữ liệu & SQLAlchemy ORM",
            lessons: [
                {
                    id: "w7",
                    title: "Ánh xạ quan hệ 1 - Nhiều giữa User, Subject và Task",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Thiết kế mô hình dữ liệu cô lập theo từng tài khoản</h5>
                        <ul>
                            <li>Một <strong>User</strong> sở hữu nhiều <strong>Subject</strong> (khóa ngoại <code>subjects.user_id</code>).</li>
                            <li>Một <strong>Subject</strong> chứa nhiều <strong>Task</strong> (khóa ngoại <code>tasks.subject_id</code>).</li>
                            <li>Khi xóa một môn học, cấu hình <code>cascade="all, delete-orphan"</code> giúp tự động dọn dẹp toàn bộ bài tập con của môn đó.</li>
                        </ul>
                    `
                },
                {
                    id: "w8",
                    title: "Truy vấn lọc, tìm kiếm & Join bảng với SQLAlchemy",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Kết hợp nhiều điều kiện lọc động</h5>
                        <ul>
                            <li>Sử dụng <code>.join(Subject).filter(Subject.user_id == current_user.id)</code> để đảm bảo sinh viên chỉ nhìn thấy bài tập của chính mình.</li>
                            <li>Tìm kiếm không phân biệt chữ hoa/thường bằng toán tử <code>Task.title.ilike(f"%{keyword}%")</code>.</li>
                        </ul>
                    `
                },
                {
                    id: "w9",
                    title: "Tính toán nghiệp vụ thời gian thực (Quá hạn & Sắp đến hạn)",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Tách biệt logic nghiệp vụ vào tầng Core</h5>
                        <ul>
                            <li>Hàm <code>is_task_overdue</code> kiểm tra bài tập chưa hoàn thành (<code>status != DONE</code>) và có hạn chót nhỏ hơn thời điểm hiện tại.</li>
                            <li>Hàm <code>is_task_due_soon</code> kiểm tra bài tập chưa hoàn thành có hạn chót nằm trong khoảng <strong>3 ngày tới</strong>.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 4: Bảo mật JWT & Lập trình Frontend",
            lessons: [
                {
                    id: "w10",
                    title: "Mã hóa mật khẩu Bcrypt & Cấp phát JWT Token",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Quy trình xác thực người dùng an toàn</h5>
                        <ul>
                            <li>Tuyệt đối không lưu mật khẩu dạng văn bản thuần trong Database; sử dụng thuật toán băm một chiều <strong>Bcrypt</strong> kèm muối ngẫu nhiên (Salt).</li>
                            <li>Khi đăng nhập đúng, Server ký một chuỗi <strong>JWT (JSON Web Token)</strong> chứa thông tin định danh và thời gian hết hạn.</li>
                        </ul>
                    `
                },
                {
                    id: "w11",
                    title: "Giao tiếp bất đồng bộ với Fetch API & Async/Await",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Gửi yêu cầu kèm Bearer Token từ trình duyệt</h5>
                        <div class="lms-code-block">const response = await fetch("http://127.0.0.1:8000/tasks/", {
    headers: {
        "Content-Type": "application/json",
        "Authorization": \`Bearer \${localStorage.getItem("access_token")}\`
    }
});
const tasks = await response.json();</div>
                        <p>Nếu Server trả về mã <code>401</code> (Token hết hạn), Frontend tự động xóa token và điều hướng về trang đăng nhập.</p>
                    `
                },
                {
                    id: "w12",
                    title: "Thao tác DOM động & Tối ưu trải nghiệm UI/UX",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Các nguyên tắc thiết kế giao diện trực quan</h5>
                        <ul>
                            <li><strong>Empty State (Trạng thái rỗng):</strong> Khi tài khoản mới chưa có dữ liệu, hiển thị thông báo hướng dẫn kèm nút hành động thay vì để bảng trắng trơn.</li>
                            <li><strong>Visual Highlight:</strong> Dùng màu đỏ cho bài quá hạn, màu vàng cho bài sắp đến hạn giúp người dùng nhận diện mức độ ưu tiên ngay lập tức.</li>
                        </ul>
                    `
                }
            ]
        }
    ],
    INT1306: [
        {
            chapter: "Chương 1: Phân tích Độ phức tạp Thuật toán",
            lessons: [
                {
                    id: "d1",
                    title: "Khái niệm Thuật toán & Ký hiệu tiệm cận Big-O",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Tại sao cần đánh giá độ phức tạp thuật toán?</h5>
                        <ul>
                            <li>Cùng một bài toán sắp xếp 1 triệu phần tử, thuật toán O(n²) mất vài phút trong khi O(n log n) chỉ mất chưa tới 0.1 giây.</li>
                            <li><strong>Big-O</strong> đo lường tốc độ tăng trưởng của số phép tính khi kích thước dữ liệu đầu vào <em>n</em> tiến ra vô cùng.</li>
                        </ul>
                        <h5>II. Thứ tự tăng trưởng phổ biến từ nhanh đến chậm</h5>
                        <ul>
                            <li><code>O(1)</code>: Truy cập phần tử mảng theo chỉ số.</li>
                            <li><code>O(log n)</code>: Tìm kiếm nhị phân trên mảng đã sắp xếp.</li>
                            <li><code>O(n)</code>: Duyệt tuyến tính một vòng lặp.</li>
                            <li><code>O(n log n)</code>: Các thuật toán sắp xếp hiệu quả (Merge Sort, Quick Sort).</li>
                            <li><code>O(n²)</code>: Hai vòng lặp lồng nhau (Bubble Sort, Selection Sort).</li>
                        </ul>
                    `
                },
                {
                    id: "d2",
                    title: "Đệ quy & Quy hoạch động cơ bản",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Cấu trúc một hàm đệ quy chuẩn</h5>
                        <ul>
                            <li><strong>Điểm neo (Base Case):</strong> Điều kiện dừng để tránh lỗi tràn bộ nhớ ngăn xếp (Stack Overflow).</li>
                            <li><strong>Bước quy nạp:</strong> Chia nhỏ bài toán lớn thành bài toán con cùng dạng có kích thước nhỏ hơn.</li>
                        </ul>
                    `
                },
                {
                    id: "d3",
                    title: "Đánh giá độ phức tạp không gian (Space Complexity)",
                    duration: "9 phút đọc",
                    content: `
                        <h5>I. Bộ nhớ phụ trợ trong thực thi</h5>
                        <ul>
                            <li>Đo lượng RAM phát sinh thêm trong quá trình chạy thuật toán (mảng phụ, bảng băm, khung ngăn xếp đệ quy).</li>
                            <li>Thuật toán tại chỗ (<em>In-place</em>) như QuickSort có độ phức tạp không gian phụ chỉ <code>O(log n)</code>.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 2: Cấu trúc Dữ liệu Tuyến tính",
            lessons: [
                {
                    id: "d4",
                    title: "Mảng động & Danh sách liên kết (Linked List)",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. So sánh Mảng (Array) và Danh sách liên kết (Linked List)</h5>
                        <ul>
                            <li><strong>Mảng:</strong> Lưu trữ liền kề trên RAM, truy cập ngẫu nhiên cực nhanh <code>O(1)</code> nhưng chèn/xóa ở giữa tốn <code>O(n)</code>.</li>
                            <li><strong>Linked List:</strong> Mỗi nút (Node) gồm dữ liệu và con trỏ <code>next</code> trỏ tới nút kế tiếp; chèn/xóa đầu danh sách chỉ mất <code>O(1)</code>.</li>
                        </ul>
                    `
                },
                {
                    id: "d5",
                    title: "Ngăn xếp (Stack - LIFO) & Ứng dụng",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Nguyên lý vào sau ra trước (Last-In, First-Out)</h5>
                        <ul>
                            <li>Các thao tác chính: <code>push()</code> (đẩy vào đỉnh), <code>pop()</code> (lấy phần tử đỉnh), <code>peek()</code> (xem phần tử đỉnh).</li>
                            <li>Ứng dụng thực tế: Kiểm tra dấu ngoặc hợp lệ, tính giá trị biểu thức hậu tố, chức năng Undo/Redo trong trình soạn thảo.</li>
                        </ul>
                    `
                },
                {
                    id: "d6",
                    title: "Hàng đợi (Queue - FIFO) & Hàng đợi ưu tiên",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Nguyên lý vào trước ra trước (First-In, First-Out)</h5>
                        <ul>
                            <li>Phần tử thêm vào ở cuối hàng (<code>enqueue</code>) và lấy ra ở đầu hàng (<code>dequeue</code>).</li>
                            <li>Ứng dụng: Lập lịch tiến trình CPU, xử lý hàng đợi yêu cầu trên máy chủ web và thuật toán duyệt đồ thị BFS.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 3: Cây & Bảng băm (Hash Table)",
            lessons: [
                {
                    id: "d7",
                    title: "Cây nhị phân tìm kiếm (Binary Search Tree)",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Tính chất của cây BST</h5>
                        <ul>
                            <li>Mọi nút thuộc cây con bên trái đều có giá trị nhỏ hơn nút gốc; mọi nút thuộc cây con bên phải đều lớn hơn nút gốc.</li>
                            <li>Thời gian tìm kiếm, thêm và xóa trung bình đạt <code>O(log n)</code>.</li>
                        </ul>
                        <h5>II. Ba phép duyệt cây kinh điển</h5>
                        <ul>
                            <li><strong>Pre-order (NLR):</strong> Gốc $\rightarrow$ Trái $\rightarrow$ Phải.</li>
                            <li><strong>In-order (LNR):</strong> Trái $\rightarrow$ Gốc $\rightarrow$ Phải (cho ra dãy số tăng dần).</li>
                            <li><strong>Post-order (LRN):</strong> Trái $\rightarrow$ Phải $\rightarrow$ Gốc.</li>
                        </ul>
                    `
                },
                {
                    id: "d8",
                    title: "Cây cân bằng AVL & Đống nhị phân (Binary Heap)",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Giữ chiều cao cây luôn cân bằng</h5>
                        <ul>
                            <li>Cây AVL duy trì chênh lệch chiều cao giữa cây con trái và phải không quá 1 đơn vị thông qua các phép xoay đơn và xoay kép.</li>
                            <li><strong>Min-Heap / Max-Heap</strong> luôn giữ phần tử nhỏ nhất hoặc lớn nhất ở gốc cây, là nền tảng của thuật toán HeapSort.</li>
                        </ul>
                    `
                },
                {
                    id: "d9",
                    title: "Bảng băm (Hash Table) & Xử lý đụng độ",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Tìm kiếm tốc độ O(1)</h5>
                        <ul>
                            <li>Hàm băm (Hash Function) biến đổi khóa (Key) thành chỉ số mảng lưu trữ giá trị (Value).</li>
                            <li>Khi hai khóa khác nhau cho cùng một chỉ số (Collision), ta xử lý bằng phương pháp <strong>Kết nối trực tiếp (Chaining)</strong> hoặc <strong>Thăm dò tuyến tính (Linear Probing)</strong>.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 4: Sắp xếp & Thuật toán Đồ thị",
            lessons: [
                {
                    id: "d10",
                    title: "QuickSort & MergeSort (Chia để trị)",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Chiến lược Chia để trị (Divide and Conquer)</h5>
                        <ul>
                            <li><strong>MergeSort:</strong> Chia đôi mảng thành hai nửa, sắp xếp từng nửa rồi trộn lại; luôn ổn định với độ phức tạp <code>O(n log n)</code>.</li>
                            <li><strong>QuickSort:</strong> Chọn một phần tử chốt (Pivot), phân hoạch các phần tử nhỏ hơn sang trái và lớn hơn sang phải.</li>
                        </ul>
                    `
                },
                {
                    id: "d11",
                    title: "Biểu diễn Đồ thị & Duyệt BFS, DFS",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Hai cách biểu diễn đồ thị trong bộ nhớ</h5>
                        <ul>
                            <li><strong>Ma trận kề (Adjacency Matrix):</strong> Tốn bộ nhớ <code>O(V²)</code>, kiểm tra cạnh nối mất <code>O(1)</code>.</li>
                            <li><strong>Danh sách kề (Adjacency List):</strong> Tiết kiệm bộ nhớ <code>O(V + E)</code>, tối ưu cho đồ thị thưa.</li>
                        </ul>
                        <h5>II. BFS và DFS</h5>
                        <ul>
                            <li><strong>BFS (Breadth-First Search):</strong> Dùng Queue để loang theo từng lớp, tìm đường đi ngắn nhất trên đồ thị không trọng số.</li>
                            <li><strong>DFS (Depth-First Search):</strong> Dùng Stack/Đệ quy đi sâu hết nhánh rồi quay lui, dùng phát hiện chu trình.</li>
                        </ul>
                    `
                },
                {
                    id: "d12",
                    title: "Thuật toán tìm đường đi ngắn nhất Dijkstra",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Nguyên lý tham lam trên đồ thị có trọng số dương</h5>
                        <ul>
                            <li>Khởi tạo khoảng cách từ đỉnh xuất phát tới chính nó bằng 0, tới các đỉnh khác bằng vô cùng.</li>
                            <li>Ở mỗi bước, chọn đỉnh chưa xét có khoảng cách nhỏ nhất và cập nhật (Relax) khoảng cách tới các đỉnh kề.</li>
                        </ul>
                    `
                }
            ]
        }
    ],
    INT1313: [
        {
            chapter: "Chương 1: Mô hình Dữ liệu Quan hệ & ERD",
            lessons: [
                {
                    id: "db1",
                    title: "Tổng quan Hệ quản trị Cơ sở dữ liệu (DBMS)",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Vai trò của CSDL quan hệ</h5>
                        <ul>
                            <li>Lưu trữ dữ liệu có cấu trúc dưới dạng các bảng (Table) gồm hàng (Bản ghi) và cột (Thuộc tính).</li>
                            <li>Đảm bảo tính nhất quán, toàn vẹn dữ liệu và hỗ trợ truy xuất đồng thời cho nhiều người dùng.</li>
                        </ul>
                    `
                },
                {
                    id: "db2",
                    title: "Thiết kế sơ đồ thực thể liên kết (ERD)",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Các thành phần chính trong sơ đồ ERD</h5>
                        <ul>
                            <li><strong>Thực thể (Entity):</strong> Đối tượng cần quản lý như <code>User</code>, <code>Subject</code>, <code>Task</code>.</li>
                            <li><strong>Khóa chính (Primary Key - PK):</strong> Thuộc tính định danh duy nhất mỗi dòng dữ liệu (không trùng lặp, không NULL).</li>
                            <li><strong>Khóa ngoại (Foreign Key - FK):</strong> Cột tham chiếu tới khóa chính của bảng khác để tạo mối liên kết.</li>
                        </ul>
                    `
                },
                {
                    id: "db3",
                    title: "Chuyển đổi từ ERD sang Lược đồ quan hệ",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Quy tắc ánh xạ quan hệ</h5>
                        <ul>
                            <li><strong>Quan hệ 1 - Nhiều (1-N):</strong> Đem khóa chính của bảng phía 1 sang làm khóa ngoại của bảng phía Nhiều.</li>
                            <li><strong>Quan hệ Nhiều - Nhiều (N-N):</strong> Tách thành một bảng trung gian chứa cặp khóa ngoại của cả hai bảng gốc.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 2: Chuẩn hóa Dữ liệu (1NF, 2NF, 3NF)",
            lessons: [
                {
                    id: "db4",
                    title: "Dị thường dữ liệu & Phụ thuộc hàm",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Tại sao bảng thiết kế kém lại gây lỗi?</h5>
                        <ul>
                            <li>Lưu trùng lặp thông tin môn học ở mọi dòng bài tập gây tốn dung lượng và dễ sai lệch khi sửa tên môn (Dị thường cập nhật).</li>
                            <li><strong>Phụ thuộc hàm X $\rightarrow$ Y:</strong> Biết giá trị của thuộc tính X sẽ xác định duy nhất giá trị của thuộc tính Y.</li>
                        </ul>
                    `
                },
                {
                    id: "db5",
                    title: "Các dạng chuẩn 1NF, 2NF và 3NF",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Tiêu chuẩn của từng mức chuẩn hóa</h5>
                        <ul>
                            <li><strong>1NF:</strong> Mọi ô dữ liệu chỉ chứa giá trị nguyên tố (không chứa danh sách nhiều giá trị trong một ô).</li>
                            <li><strong>2NF:</strong> Đạt 1NF và mọi thuộc tính không khóa phải phụ thuộc đầy đủ vào toàn bộ khóa chính.</li>
                            <li><strong>3NF:</strong> Đạt 2NF và không có thuộc tính không khóa nào phụ thuộc bắc cầu qua một thuộc tính không khóa khác.</li>
                        </ul>
                    `
                },
                {
                    id: "db6",
                    title: "Thực hành phân rã lược đồ đạt chuẩn 3NF",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Quy trình chuẩn hóa thực tế</h5>
                        <ul>
                            <li>Tách các nhóm thuộc tính phụ thuộc riêng biệt ra thành bảng độc lập và nối lại bằng khóa ngoại để bảo toàn thông tin không mất mát.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 3: Ngôn ngữ Truy vấn SQL",
            lessons: [
                {
                    id: "db7",
                    title: "Nhóm lệnh DDL & DML cơ bản",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Định nghĩa và thao tác dữ liệu</h5>
                        <ul>
                            <li><strong>DDL:</strong> <code>CREATE TABLE</code>, <code>ALTER TABLE</code>, <code>DROP TABLE</code> dùng để tạo và sửa cấu trúc bảng.</li>
                            <li><strong>DML:</strong> <code>INSERT INTO</code>, <code>UPDATE</code>, <code>DELETE</code> dùng để thêm, sửa, xóa bản ghi.</li>
                        </ul>
                    `
                },
                {
                    id: "db8",
                    title: "Truy vấn kết nối bảng (INNER JOIN, LEFT JOIN)",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Kết hợp dữ liệu từ nhiều bảng</h5>
                        <div class="lms-code-block">SELECT s.code, s.name, COUNT(t.id) AS total_tasks
FROM subjects s
LEFT JOIN tasks t ON s.id = t.subject_id
GROUP BY s.id, s.code, s.name;</div>
                        <p><code>LEFT JOIN</code> giữ lại cả những môn học chưa có bài tập nào (trả về số lượng là 0).</p>
                    `
                },
                {
                    id: "db9",
                    title: "Gom nhóm dữ liệu với GROUP BY, HAVING & Subquery",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Phân biệt WHERE và HAVING</h5>
                        <ul>
                            <li><code>WHERE</code> lọc từng dòng dữ liệu thô trước khi gom nhóm.</li>
                            <li><code>HAVING</code> lọc kết quả sau khi đã tính toán các hàm tổng hợp <code>COUNT()</code>, <code>SUM()</code>, <code>AVG()</code>.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 4: Chỉ mục & Giao dịch ACID",
            lessons: [
                {
                    id: "db10",
                    title: "Tối ưu tốc độ truy vấn với Index (B-Tree)",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Cơ chế hoạt động của Index</h5>
                        <ul>
                            <li>Index tạo ra cấu trúc cây tìm kiếm cân bằng giúp Database tìm bản ghi mà không cần quét toàn bộ bảng (Full Table Scan).</li>
                            <li>Nên đánh Index trên các cột thường xuyên xuất hiện trong mệnh đề <code>WHERE</code>, <code>JOIN</code> và <code>ORDER BY</code>.</li>
                        </ul>
                    `
                },
                {
                    id: "db11",
                    title: "Giao dịch (Transaction) & 4 tính chất ACID",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Đảm bảo an toàn dữ liệu tuyệt đối</h5>
                        <ul>
                            <li><strong>Atomicity (Nguyên tử):</strong> Hoặc thực hiện thành công toàn bộ lệnh, hoặc hoàn tác (Rollback) tất cả nếu gặp lỗi.</li>
                            <li><strong>Consistency (Nhất quán):</strong> Dữ liệu luôn thỏa mãn mọi ràng buộc toàn vẹn trước và sau giao dịch.</li>
                            <li><strong>Isolation (Cô lập):</strong> Các giao dịch chạy đồng thời không làm sai lệch dữ liệu của nhau.</li>
                            <li><strong>Durability (Bền vững):</strong> Dữ liệu đã <code>COMMIT</code> sẽ được lưu vĩnh viễn ngay cả khi mất điện.</li>
                        </ul>
                    `
                },
                {
                    id: "db12",
                    title: "Sao lưu & Bảo mật quyền truy cập Database",
                    duration: "9 phút đọc",
                    content: `
                        <h5>I. Nguyên tắc phân quyền tối thiểu</h5>
                        <ul>
                            <li>Tạo tài khoản ứng dụng riêng biệt chỉ cấp quyền <code>SELECT, INSERT, UPDATE, DELETE</code> thay vì dùng tài khoản quản trị tối cao <code>root</code>.</li>
                        </ul>
                    `
                }
            ]
        }
    ],
    BAS1150: [
        {
            chapter: "Chương 1: Tổng quan Trí tuệ nhân tạo",
            lessons: [
                {
                    id: "ai1",
                    title: "Phân biệt AI, Machine Learning và Deep Learning",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Bức tranh toàn cảnh về Trí tuệ nhân tạo</h5>
                        <ul>
                            <li><strong>Artificial Intelligence (AI):</strong> Khoa học chế tạo máy móc có khả năng suy luận và giải quyết vấn đề như con người.</li>
                            <li><strong>Machine Learning (Học máy):</strong> Nhánh cốt lõi của AI cho phép máy tự học quy luật từ dữ liệu thay vì lập trình cứng từng câu lệnh <code>if-else</code>.</li>
                            <li><strong>Deep Learning (Học sâu):</strong> Sử dụng mạng nơ-ron nhân tạo nhiều lớp để xử lý dữ liệu phi cấu trúc như hình ảnh, giọng nói, văn bản.</li>
                        </ul>
                    `
                },
                {
                    id: "ai2",
                    title: "Quy trình xây dựng một dự án AI thực tế",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. 6 bước chuẩn trong vòng đời mô hình</h5>
                        <ul>
                            <li>1. Xác định bài toán & chỉ số đánh giá $\rightarrow$ 2. Thu thập dữ liệu $\rightarrow$ 3. Tiền xử lý & làm sạch $\rightarrow$ 4. Huấn luyện mô hình $\rightarrow$ 5. Đánh giá & tinh chỉnh $\rightarrow$ 6. Triển khai API vào ứng dụng.</li>
                        </ul>
                    `
                },
                {
                    id: "ai3",
                    title: "Các bài toán ứng dụng AI trong giáo dục & đời sống",
                    duration: "9 phút đọc",
                    content: `
                        <h5>I. Ứng dụng tiêu biểu</h5>
                        <ul>
                            <li>Hệ thống gợi ý lộ trình học tập cá nhân hóa, dự đoán nguy cơ trễ hạn bài tập, tóm tắt tài liệu tự động và trợ lý hỏi đáp học thuật.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 2: Tiền xử lý Dữ liệu",
            lessons: [
                {
                    id: "ai4",
                    title: "Làm sạch dữ liệu khuyết thiếu & Nhiễu",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Dữ liệu sạch quyết định 80% chất lượng mô hình</h5>
                        <ul>
                            <li>Xử lý giá trị bị thiếu (Missing Values) bằng cách điền giá trị trung bình (Mean), trung vị (Median) hoặc loại bỏ dòng nhiễu.</li>
                            <li>Phát hiện giá trị ngoại lai (Outliers) bằng biểu đồ Boxplot hoặc quy tắc IQR.</li>
                        </ul>
                    `
                },
                {
                    id: "ai5",
                    title: "Chuẩn hóa đặc trưng & Mã hóa dữ liệu",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Đưa các đặc trưng về cùng thang đo</h5>
                        <ul>
                            <li><strong>Min-Max Scaling:</strong> Co giãn dữ liệu về đoạn <code>[0, 1]</code>.</li>
                            <li><strong>Standardization (Z-Score):</strong> Đưa dữ liệu về phân phối có trung bình bằng 0 và độ lệch chuẩn bằng 1.</li>
                            <li><strong>One-Hot Encoding:</strong> Chuyển dữ liệu dạng chữ (như trạng thái <code>TODO, DONE</code>) thành véc-tơ nhị phân 0/1.</li>
                        </ul>
                    `
                },
                {
                    id: "ai6",
                    title: "Chia tập Train / Validation / Test & Chống Overfitting",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Đánh giá khách quan khả năng tổng quát hóa</h5>
                        <ul>
                            <li>Chia dữ liệu theo tỷ lệ phổ biến <strong>70% Train - 15% Validation - 15% Test</strong>.</li>
                            <li><strong>Overfitting (Học vẹt):</strong> Mô hình đạt điểm rất cao trên tập Train nhưng dự đoán kém trên dữ liệu mới.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 3: Các thuật toán Học máy cốt lõi",
            lessons: [
                {
                    id: "ai7",
                    title: "Hồi quy tuyến tính (Linear Regression)",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Dự đoán giá trị liên tục</h5>
                        <ul>
                            <li>Tìm đường thẳng (hoặc siêu phẳng) tối ưu biểu diễn mối quan hệ giữa biến đầu vào và kết quả đầu ra bằng phương pháp tối thiểu hóa sai số bình phương trung bình (MSE).</li>
                        </ul>
                    `
                },
                {
                    id: "ai8",
                    title: "Phân loại với Logistic Regression & Decision Tree",
                    duration: "12 phút đọc",
                    content: `
                        <h5>I. Bài toán phân lớp dữ liệu</h5>
                        <ul>
                            <li><strong>Logistic Regression:</strong> Sử dụng hàm Sigmoid đưa đầu ra về xác suất trong khoảng <code>(0, 1)</code> để phân loại nhị phân.</li>
                            <li><strong>Decision Tree & Random Forest:</strong> Xây dựng tập hợp nhiều cây quyết định bỏ phiếu đa số giúp tăng độ chính xác và giảm nhiễu.</li>
                        </ul>
                    `
                },
                {
                    id: "ai9",
                    title: "Thước đo đánh giá: Accuracy, Precision, Recall & F1-Score",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Đọc hiểu Ma trận nhầm lẫn (Confusion Matrix)</h5>
                        <ul>
                            <li><strong>Precision:</strong> Trong các mẫu mô hình dự đoán là Dương tính, có bao nhiêu phần trăm thực sự đúng.</li>
                            <li><strong>Recall:</strong> Trong tổng số mẫu Dương tính thực tế, mô hình phát hiện được bao nhiêu phần trăm.</li>
                            <li><strong>F1-Score:</strong> Trung bình điều hòa cân bằng giữa Precision và Recall.</li>
                        </ul>
                    `
                }
            ]
        },
        {
            chapter: "Chương 4: Triển khai Mô hình AI vào Web",
            lessons: [
                {
                    id: "ai10",
                    title: "Đóng gói mô hình với Joblib / Pickle",
                    duration: "10 phút đọc",
                    content: `
                        <h5>I. Lưu trữ trọng số sau huấn luyện</h5>
                        <ul>
                            <li>Sau khi huấn luyện xong, lưu toàn bộ tham số mô hình ra tệp <code>.pkl</code> hoặc <code>.joblib</code> để nạp lại tức thì khi khởi động máy chủ web.</li>
                        </ul>
                    `
                },
                {
                    id: "ai11",
                    title: "Xây dựng API dự đoán bằng FastAPI",
                    duration: "11 phút đọc",
                    content: `
                        <h5>I. Kết nối mô hình AI với hệ thống Backend</h5>
                        <div class="lms-code-block">@router.post("/predict-risk")
def predict_deadline_risk(data: TaskFeatureInput):
    score = model.predict_proba([[data.days_left, data.pending_tasks]])[0][1]
    return {"risk_probability": round(float(score), 2)}</div>
                    `
                },
                {
                    id: "ai12",
                    title: "Giám sát mô hình & Cải tiến liên tục",
                    duration: "9 phút đọc",
                    content: `
                        <h5>I. Duy trì độ chính xác theo thời gian</h5>
                        <ul>
                            <li>Thu thập phản hồi thực tế từ người dùng để tái huấn luyện định kỳ, tránh hiện tượng suy giảm độ chính xác khi dữ liệu thay đổi (Data Drift).</li>
                        </ul>
                    `
                }
            ]
        }
    ]
};

const params = new URLSearchParams(window.location.search);
let subjectId = Number(params.get("subject_id")) || null;
let currentSubject = null;
let chapters = [];
let flatLessons = [];
let activeLessonIndex = 0;

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

function showAlert(message, type) {
    const alertMsg = document.getElementById("alertMessage");
    alertMsg.className = `alert alert-${type}`;
    alertMsg.innerText = message;
    alertMsg.classList.remove("d-none");
    setTimeout(() => alertMsg.classList.add("d-none"), 4000);
}

function buildFallbackCurriculum(subject) {
    const name = subject.name || "Học phần chuyên ngành";
    const desc = subject.description || `Kiến thức trọng tâm và phương pháp thực hành môn ${name}.`;
    return [
        {
            chapter: `Chương 1: Tổng quan & Nền tảng ${name}`,
            lessons: [
                {
                    id: "c1_1",
                    title: `Giới thiệu mục tiêu và chuẩn đầu ra môn ${name}`,
                    duration: "10 phút đọc",
                    content: `<h5>I. Mục tiêu học phần</h5><ul><li>Nắm vững hệ thống khái niệm cốt lõi của <strong>${name}</strong>.</li><li>${desc}</li></ul><h5>II. Phương pháp học tập hiệu quả</h5><ul><li>Đọc kỹ lý thuyết từng chương, ghi chú lại các từ khóa trọng tâm và tạo bài tập ôn luyện ngay sau mỗi buổi học.</li></ul>`
                },
                {
                    id: "c1_2",
                    title: `Các khái niệm và thuật ngữ nền tảng`,
                    duration: "11 phút đọc",
                    content: `<h5>I. Hệ thống thuật ngữ cơ bản</h5><ul><li>Hiểu rõ bản chất và phạm vi ứng dụng của từng thành phần trong kiến trúc môn học.</li><li>Phân biệt các khái niệm dễ nhầm lẫn thông qua ví dụ thực tế.</li></ul>`
                },
                {
                    id: "c1_3",
                    title: `Thiết lập môi trường & Công cụ thực hành`,
                    duration: "9 phút đọc",
                    content: `<h5>I. Chuẩn bị công cụ làm việc</h5><ul><li>Cài đặt đầy đủ phần mềm, thư viện cần thiết và kiểm tra môi trường chạy thử nghiệm trước khi bước vào các chương chuyên sâu.</li></ul>`
                }
            ]
        },
        {
            chapter: `Chương 2: Nguyên lý & Kỹ thuật cốt lõi`,
            lessons: [
                {
                    id: "c2_1",
                    title: `Phân tích quy trình hoạt động chuẩn`,
                    duration: "12 phút đọc",
                    content: `<h5>I. Luồng xử lý dữ liệu và nghiệp vụ</h5><ul><li>Trình bày từng bước vận hành từ đầu vào, xử lý trung gian cho đến kết quả đầu ra.</li><li>Đánh giá ưu nhược điểm của từng phương pháp tiếp cận.</li></ul>`
                },
                {
                    id: "c2_2",
                    title: `Kỹ thuật tối ưu và xử lý tình huống biên`,
                    duration: "11 phút đọc",
                    content: `<h5>I. Xử lý ngoại lệ trong thực tế</h5><ul><li>Nhận diện các lỗi thường gặp khi triển khai và cách phòng tránh ngay từ bước thiết kế.</li></ul>`
                },
                {
                    id: "c2_3",
                    title: `Ví dụ minh họa từng bước`,
                    duration: "10 phút đọc",
                    content: `<h5>I. Bài toán mẫu điển hình</h5><ul><li>Áp dụng trực tiếp lý thuyết vừa học để giải quyết một tình huống cụ thể từ đầu đến cuối.</li></ul>`
                }
            ]
        },
        {
            chapter: `Chương 3: Ứng dụng & Thực hành chuyên sâu`,
            lessons: [
                {
                    id: "c3_1",
                    title: `Xây dựng giải pháp hoàn chỉnh`,
                    duration: "12 phút đọc",
                    content: `<h5>I. Tích hợp các thành phần</h5><ul><li>Kết nối kiến thức của Chương 1 và Chương 2 thành một quy trình hoàn chỉnh đáp ứng yêu cầu thực tế.</li></ul>`
                },
                {
                    id: "c3_2",
                    title: `Kiểm thử, đánh giá và tối ưu hiệu năng`,
                    duration: "10 phút đọc",
                    content: `<h5>I. Tiêu chí đánh giá chất lượng</h5><ul><li>Kiểm tra tính chính xác, tốc độ xử lý và khả năng mở rộng của giải pháp.</li></ul>`
                },
                {
                    id: "c3_3",
                    title: `Tổng kết kiến thức & Ôn tập kiểm tra`,
                    duration: "10 phút đọc",
                    content: `<h5>I. Hệ thống hóa toàn bộ học phần</h5><ul><li>Rà soát lại toàn bộ kiến thức trọng tâm của <strong>${name}</strong> để sẵn sàng cho bài đánh giá cuối kỳ.</li></ul>`
                }
            ]
        }
    ];
}

function getCompletedStorageKey() {
    const keyPart = (currentSubject.code || currentSubject.id).toString().toUpperCase();
    return `studenthub_lms_done_${keyPart}`;
}

function getCompletedIds() {
    try {
        const raw = localStorage.getItem(getCompletedStorageKey());
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

function saveCompletedIds(ids) {
    localStorage.setItem(getCompletedStorageKey(), JSON.stringify(ids));
}

function renderSidebarAndProgress() {
    const completedIds = getCompletedIds();
    const totalLessons = flatLessons.length;
    const doneCount = flatLessons.filter(item => completedIds.includes(item.lesson.id)).length;
    const pct = totalLessons > 0 ? Math.round((doneCount / totalLessons) * 100) : 0;

    document.getElementById("xpBadge").innerText = `⭐ ${doneCount * 25} XP`;
    document.getElementById("bottomProgressPct").innerText = `${pct}%`;
    document.getElementById("bottomProgressBar").style.width = `${pct}%`;
    document.getElementById("bottomProgressCount").innerText = `(${doneCount}/${totalLessons} bài học)`;

    const tree = document.getElementById("curriculumTree");
    tree.innerHTML = "";

    let globalIdx = 0;
    chapters.forEach((chap, cIdx) => {
        const chapDone = chap.lessons.filter(l => completedIds.includes(l.id)).length;
        const containsActive = chap.lessons.some(l => flatLessons[activeLessonIndex]?.lesson.id === l.id);

        let lessonsHtml = "";
        chap.lessons.forEach(lesson => {
            const idx = globalIdx++;
            const isDone = completedIds.includes(lesson.id);
            const isActive = idx === activeLessonIndex;
            const statusIcon = isDone ? "✓" : (isActive ? "▶" : (idx + 1));

            lessonsHtml += `
                <button type="button" class="lms-lesson-item ${isDone ? "done" : ""} ${isActive ? "active" : ""}" onclick="selectLesson(${idx})">
                    <span class="lms-lesson-status">${statusIcon}</span>
                    <div class="overflow-hidden">
                        <div class="small fw-semibold text-dark">${lesson.title}</div>
                        <div class="text-muted" style="font-size: 0.76rem;">📖 ${lesson.duration}</div>
                    </div>
                </button>
            `;
        });

        tree.innerHTML += `
            <div class="lms-chapter-box">
                <button type="button" class="lms-chapter-header" onclick="toggleChapter(${cIdx})">
                    <div class="d-flex align-items-center gap-2 overflow-hidden">
                        <span class="lms-chapter-num">${cIdx + 1}</span>
                        <div class="overflow-hidden">
                            <div class="small fw-bold text-primary text-truncate">${chap.chapter}</div>
                            <div class="text-muted" style="font-size: 0.76rem;">${chap.lessons.length} bài học • ${chapDone} hoàn thành</div>
                        </div>
                    </div>
                    <span class="text-muted small">▾</span>
                </button>
                <div class="lms-lesson-list ${containsActive ? "" : ""}" id="chapterList_${cIdx}">
                    ${lessonsHtml}
                </div>
            </div>
        `;
    });
}

function toggleChapter(chapterIndex) {
    const el = document.getElementById(`chapterList_${chapterIndex}`);
    if (el) el.classList.toggle("collapsed");
}

function selectLesson(index) {
    if (index < 0 || index >= flatLessons.length) return;
    activeLessonIndex = index;

    const current = flatLessons[index];
    const completedIds = getCompletedIds();
    const isDone = completedIds.includes(current.lesson.id);

    document.getElementById("topBreadcrumb").innerText = `[${currentSubject.code}] ${currentSubject.name} • ${current.chapter}`;
    document.getElementById("topLessonTitle").innerText = current.lesson.title;
    document.getElementById("articleChapterTag").innerText = current.chapter;
    document.getElementById("articleTitle").innerText = `[Bài đọc] ${current.lesson.title}`;
    document.getElementById("articleMeta").innerText = `Thời lượng: ${current.lesson.duration} • Trạng thái: ${isDone ? "Đã hoàn thành" : "Đang học"}`;
    document.getElementById("articleBody").innerHTML = current.lesson.content;

    document.getElementById("prevLessonBtn").disabled = index === 0;
    const completeBtn = document.getElementById("completeLessonBtn");
    completeBtn.innerText = isDone
        ? (index < flatLessons.length - 1 ? "Tiếp tục bài tiếp theo →" : "Đã hoàn thành khóa học ✓")
        : "Hoàn thành bài học 🎉";

    renderSidebarAndProgress();

    const scrollArea = document.getElementById("readerScrollArea");
    if (scrollArea) scrollArea.scrollTo({ top: 0, behavior: "smooth" });
}

function handleCompleteLesson() {
    const current = flatLessons[activeLessonIndex];
    if (!current) return;

    const completedIds = getCompletedIds();
    if (!completedIds.includes(current.lesson.id)) {
        completedIds.push(current.lesson.id);
        saveCompletedIds(completedIds);
    }

    if (activeLessonIndex < flatLessons.length - 1) {
        selectLesson(activeLessonIndex + 1);
    } else {
        selectLesson(activeLessonIndex);
        showAlert("Chúc mừng! Bạn đã hoàn thành toàn bộ bài đọc của môn học này!", "success");
    }
}

async function createTaskFromCurrentLesson() {
    if (!currentSubject || !flatLessons[activeLessonIndex]) return;
    const current = flatLessons[activeLessonIndex];

    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 3);
    const dueStr = `${dueDate.getFullYear()}-${String(dueDate.getMonth() + 1).padStart(2, "0")}-${String(dueDate.getDate()).padStart(2, "0")}`;

    try {
        const response = await fetch(TASK_API_URL, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                subject_id: currentSubject.id,
                title: `Ôn tập: ${current.lesson.title}`,
                description: `Ôn tập nội dung ${current.chapter} - Môn ${currentSubject.name}`,
                due_date: dueStr,
                status: "TODO"
            })
        });

        if (response.ok) {
            showAlert(`Đã tạo bài tập "${current.lesson.title}" (Hạn 3 ngày tới) trong danh sách Bài tập!`, "success");
        } else {
            showAlert("Không thể tạo bài tập ôn luyện!", "danger");
        }
    } catch (err) {
        showAlert("Chưa kết nối được tới máy chủ FastAPI!", "danger");
    }
}

async function initCourseReader() {
    try {
        const response = await fetch(SUBJECT_API_URL, { headers: getAuthHeaders() });
        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/static/login.html";
            return;
        }

        const subjects = await response.json();
        if (!Array.isArray(subjects) || subjects.length === 0) {
            window.location.href = "/static/subjects.html";
            return;
        }

        currentSubject = subjectId
            ? (subjects.find(s => s.id === subjectId) || subjects[0])
            : subjects[0];

        const code = (currentSubject.code || "").trim().toUpperCase();
        chapters = COURSE_CURRICULUM[code] || buildFallbackCurriculum(currentSubject);

        flatLessons = [];
        chapters.forEach(chap => {
            chap.lessons.forEach(lesson => {
                flatLessons.push({ chapter: chap.chapter, lesson });
            });
        });

        document.getElementById("sidebarSubjectCode").innerText = currentSubject.code || `MÔN #${currentSubject.id}`;
        document.getElementById("sidebarSubjectName").innerText = currentSubject.name;
        document.getElementById("sidebarCourseStats").innerText = `• ${chapters.length} chương • ${flatLessons.length} bài đọc`;

        const completedIds = getCompletedIds();
        const firstUnread = flatLessons.findIndex(item => !completedIds.includes(item.lesson.id));
        selectLesson(firstUnread !== -1 ? firstUnread : 0);
    } catch (err) {
        showAlert("Không tải được dữ liệu môn học. Hãy đảm bảo server FastAPI đang chạy!", "danger");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initCourseReader();

    document.getElementById("prevLessonBtn").addEventListener("click", () => {
        if (activeLessonIndex > 0) selectLesson(activeLessonIndex - 1);
    });

    document.getElementById("completeLessonBtn").addEventListener("click", handleCompleteLesson);
    document.getElementById("createTaskFromCurrentBtn").addEventListener("click", createTaskFromCurrentLesson);
    document.getElementById("closeTipBtn").addEventListener("click", () => {
        document.getElementById("tipBanner").classList.add("d-none");
    });
});