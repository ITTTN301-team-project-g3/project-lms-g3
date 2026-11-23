const SUBJECT_API_URL = "http://127.0.0.1:8000/subjects/";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/static/login.html";
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

function updateSubjectCounters(count) {
    const heroCount = document.getElementById("totalSubjectsHero");
    const tableCount = document.getElementById("tableSubjectCount");
    if (heroCount) heroCount.innerText = count;
    if (tableCount) tableCount.innerText = `${count} môn học`;
}

function renderEmptyTable(title, subtitle) {
    updateSubjectCounters(0);
    const tbody = document.getElementById("subjectTableBody");
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-5">
                <p class="text-dark fw-semibold mb-1">${title}</p>
                <p class="text-muted small mb-0">${subtitle}</p>
            </td>
        </tr>
    `;
}

function formatApiError(data) {
    if (!data || !data.detail) return "Dữ liệu gửi lên chưa đúng định dạng!";
    if (Array.isArray(data.detail)) {
        return data.detail.map(e => `${e.loc ? e.loc.slice(-1)[0] : ""}: ${e.msg}`).join(" | ");
    }
    return data.detail;
}

function getCompletedLessonCount(subject) {
    try {
        const keyPart = (subject.code || subject.id).toString().toUpperCase();
        const raw = localStorage.getItem(`studenthub_lms_done_${keyPart}`);
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed.length : 0;
    } catch (e) {
        return 0;
    }
}

async function fetchSubjects() {
    try {
        const response = await fetch(SUBJECT_API_URL, { headers: getAuthHeaders() });

        if (response.status === 401) {
            logout();
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            renderEmptyTable("Không tải được danh sách môn học", formatApiError(data));
            return;
        }

        if (!Array.isArray(data) || data.length === 0) {
            renderEmptyTable(
                "Chưa có môn học nào trong danh sách",
                "Nhập thông tin ở khung phía trên hoặc bấm nút \"✨ Thêm nhanh 4 môn học mẫu\" trên thanh tiêu đề."
            );
            return;
        }

        updateSubjectCounters(data.length);

        const tbody = document.getElementById("subjectTableBody");
        tbody.innerHTML = "";

        data.forEach((sub, index) => {
            const code = sub.code || sub.subject_code || "---";
            const name = sub.name || sub.subject_name || sub.title || "---";
            const doneCount = getCompletedLessonCount(sub);

            tbody.innerHTML += `
                <tr style="animation-delay: ${index * 0.05}s">
                    <td class="text-muted fw-medium">#${sub.id}</td>
                    <td><span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 px-2 py-1">${code}</span></td>
                    <td>
                        <a href="/static/course.html?subject_id=${sub.id}" class="fw-semibold text-dark text-decoration-none">${name}</a>
                        <div class="small text-muted">4 chương • 12 bài đọc • Đã xong ${doneCount}/12 bài</div>
                    </td>
                    <td class="text-muted">${sub.description || "Không có mô tả"}</td>
                    <td class="text-end">
                        <a href="/static/course.html?subject_id=${sub.id}" class="btn btn-sm btn-primary me-1">📖 Vào học ngay</a>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteSubject(${sub.id})">Xóa</button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        renderEmptyTable(
            "Chưa kết nối được tới máy chủ Backend",
            "Hãy mở Terminal và chạy lệnh: uvicorn main:app --reload"
        );
        showAlert("Không kết nối được tới cổng 8000. Hãy kiểm tra xem server FastAPI đã chạy chưa!", "danger");
    }
}

async function createSubject(event) {
    event.preventDefault();

    const code = document.getElementById("subjectCode").value.trim();
    const name = document.getElementById("subjectName").value.trim();
    const description = document.getElementById("subjectDescription").value.trim();

    if (!code || !name) {
        showAlert("Vui lòng nhập đầy đủ Mã môn học và Tên môn học!", "warning");
        return;
    }

    try {
        const response = await fetch(SUBJECT_API_URL, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                code: code,
                name: name,
                description: description || null
            })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(`Đã thêm môn "${code} - ${name}" thành công!`, "success");
            document.getElementById("subjectForm").reset();
            fetchSubjects();
        } else {
            showAlert(`Không thể thêm môn học: ${formatApiError(data)}`, "danger");
        }
    } catch (err) {
        showAlert("Lỗi kết nối tới máy chủ FastAPI!", "danger");
    }
}

async function seedSampleSubjects() {
    const sampleSubjects = [
        { code: "INT1434", name: "Lập trình Web", description: "Xây dựng ứng dụng web với FastAPI và JavaScript" },
        { code: "INT1306", name: "Cấu trúc dữ liệu và Giải thuật", description: "Học phần cơ sở ngành Công nghệ thông tin" },
        { code: "INT1313", name: "Cơ sở dữ liệu", description: "Thiết kế ERD và truy vấn SQL với MySQL" },
        { code: "BAS1150", name: "Trí tuệ nhân tạo ứng dụng", description: "Nhập môn AI và các bài toán ứng dụng thực tế" }
    ];

    const btn = document.getElementById("seedSubjectsBtn");
    btn.disabled = true;
    btn.innerText = "Đang tạo...";

    let createdCount = 0;
    let lastError = "";

    for (const sub of sampleSubjects) {
        try {
            const res = await fetch(SUBJECT_API_URL, {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify(sub)
            });
            if (res.ok) {
                createdCount++;
            } else {
                const errData = await res.json();
                lastError = formatApiError(errData);
            }
        } catch (err) {
            lastError = "Chưa bật server FastAPI (uvicorn main:app --reload)";
        }
    }

    btn.disabled = false;
    btn.innerText = "✨ Thêm nhanh 4 môn học mẫu";

    if (createdCount > 0) {
        showAlert(`Đã tạo thành công ${createdCount} môn học mẫu kèm nội dung bài giảng!`, "success");
        fetchSubjects();
    } else {
        showAlert(`Chưa tạo được môn mẫu: ${lastError}`, "danger");
    }
}

async function deleteSubject(id) {
    if (!confirm("Xóa môn học sẽ xóa luôn các bài tập thuộc môn này. Bạn có chắc chắn không?")) return;

    try {
        const response = await fetch(`${SUBJECT_API_URL}${id}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (response.ok || response.status === 204) {
            showAlert("Đã xóa môn học thành công!", "success");
            fetchSubjects();
        } else {
            const data = await response.json();
            showAlert(formatApiError(data), "danger");
        }
    } catch (err) {
        showAlert("Lỗi kết nối máy chủ!", "danger");
    }
}

function showAlert(message, type) {
    const alertMsg = document.getElementById("alertMessage");
    alertMsg.className = `alert alert-${type}`;
    alertMsg.innerText = message;
    alertMsg.classList.remove("d-none");
    setTimeout(() => alertMsg.classList.add("d-none"), 5000);
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    fetchSubjects();
    document.getElementById("subjectForm").addEventListener("submit", createSubject);
    document.getElementById("seedSubjectsBtn").addEventListener("click", seedSampleSubjects);
    document.getElementById("logoutBtn").addEventListener("click", logout);
});