const API_URL = "http://127.0.0.1:8000/tasks/";
const SUBJECT_API_URL = "http://127.0.0.1:8000/subjects/";
const token = localStorage.getItem("access_token");

if (!token) {
    alert("Vui lòng đăng nhập trước!");
    window.location.href = "/static/login.html";
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// Tải danh sách môn học đưa vào ô lọc
async function loadSubjectsForFilter() {
    try {
        const response = await fetch(SUBJECT_API_URL, { headers: getAuthHeaders() });
        if (!response.ok) return;

        const subjects = await response.json();
        const subjectSelect = document.getElementById("subjectFilter");

        subjects.forEach(sub => {
            subjectSelect.innerHTML += `<option value="${sub.id}">${sub.code} - ${sub.name}</option>`;
        });
    } catch (err) {
        console.error("Lỗi tải danh sách môn học:", err);
    }
}

// Hàm xác định màu cảnh báo trực quan (Highlight UI) đồng bộ với logic Backend
function getDeadlineHighlight(task) {
    // 1. Nếu bài tập đã hoàn thành -> tô màu xanh nhẹ, không cảnh báo trễ hạn
    if (task.status === "DONE") {
        return {
            rowClass: "task-done",
            deadlineBadge: `<span class="badge bg-success ms-1">Đã xong</span>`,
            isOverdue: false,
            isDueSoon: false
        };
    }

    const rawDate = task.due_date || task.deadline;
    let diffDays = null;

    if (rawDate) {
        // Đưa cả ngày hôm nay và ngày hạn chót về 00:00:00 để tính số ngày hiển thị trên nhãn
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const dueDate = new Date(rawDate);
        dueDate.setHours(0, 0, 0, 0);

        diffDays = Math.round((dueDate - today) / (1000 * 60 * 60 * 24));
    }

    // 2. Kiểm tra quá hạn (ưu tiên cờ is_overdue từ Backend trả về) -> Cảnh báo Đỏ
    const overdue = typeof task.is_overdue === "boolean"
        ? task.is_overdue
        : (diffDays !== null && diffDays < 0);

    if (overdue) {
        const overdueText = (diffDays !== null && diffDays < 0)
            ? `Quá hạn ${Math.abs(diffDays)} ngày`
            : "Quá hạn";

        return {
            rowClass: "table-danger task-overdue",
            deadlineBadge: `<span class="badge bg-danger ms-1">${overdueText}</span>`,
            isOverdue: true,
            isDueSoon: false
        };
    }

    // 3. Kiểm tra sắp đến hạn trong 3 ngày (ưu tiên cờ is_due_soon từ Backend trả về) -> Cảnh báo Vàng
    const dueSoon = typeof task.is_due_soon === "boolean"
        ? task.is_due_soon
        : (diffDays !== null && diffDays >= 0 && diffDays <= 3);

    if (dueSoon) {
        let dueSoonText = "Sắp đến hạn";
        if (diffDays === 0) dueSoonText = "Hạn hôm nay";
        else if (diffDays !== null && diffDays > 0) dueSoonText = `Còn ${diffDays} ngày`;

        return {
            rowClass: "table-warning task-due-soon",
            deadlineBadge: `<span class="badge bg-warning text-dark ms-1">${dueSoonText}</span>`,
            isOverdue: false,
            isDueSoon: true
        };
    }

    // 4. Còn nhiều thời gian -> Hiển thị bình thường
    return { rowClass: "", deadlineBadge: "", isOverdue: false, isDueSoon: false };
}

// Cập nhật thanh banner cảnh báo tổng hợp phía trên bảng
function updateWarningBanner(overdueCount, dueSoonCount) {
    const banner = document.getElementById("deadlineWarningBanner");

    if (overdueCount === 0 && dueSoonCount === 0) {
        banner.classList.add("d-none");
        return;
    }

    const parts = [];
    if (overdueCount > 0) parts.push(`<strong>${overdueCount}</strong> bài tập đã quá hạn`);
    if (dueSoonCount > 0) parts.push(`<strong>${dueSoonCount}</strong> bài tập sắp đến hạn`);

    banner.className = overdueCount > 0
        ? "alert alert-danger shadow-sm mb-4"
        : "alert alert-warning shadow-sm mb-4";
    banner.innerHTML = `⚠️ <strong>Lưu ý tiến độ:</strong> Bạn hiện có ${parts.join(" và ")}. Hãy ưu tiên hoàn thành sớm!`;
    banner.classList.remove("d-none");
}

// Lấy danh sách bài tập từ Backend và vẽ lên bảng
async function fetchTasks() {
    try {
        const search = document.getElementById("searchInput").value.trim();
        const status = document.getElementById("statusFilter").value;
        const subjectId = document.getElementById("subjectFilter").value;

        const params = new URLSearchParams();
        if (search) params.append("search", search);
        if (status) params.append("status", status);
        if (subjectId) params.append("subject_id", subjectId);

        const requestUrl = params.toString() ? `${API_URL}?${params.toString()}` : API_URL;
        const response = await fetch(requestUrl, { headers: getAuthHeaders() });

        if (response.status === 401) {
            logout();
            return;
        }

        const tasks = await response.json();
        const tbody = document.getElementById("taskTableBody");
        tbody.innerHTML = "";

        if (!Array.isArray(tasks) || tasks.length === 0) {
            updateWarningBanner(0, 0);
            const isFiltering = Boolean(search || status || subjectId);

            if (isFiltering) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            Không tìm thấy bài tập nào phù hợp với điều kiện lọc.
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-5">
                            <p class="text-muted mb-2 fw-bold">Tài khoản của bạn hiện chưa có bài tập nào!</p>
                            <p class="text-muted small mb-3">Hãy tạo môn học trước, sau đó thêm bài tập đầu tiên để bắt đầu quản lý tiến độ.</p>
                            <a href="/static/subjects.html" class="btn btn-primary btn-sm">+ Tạo môn học ngay</a>
                        </td>
                    </tr>
                `;
            }
            return;
        }

        let overdueCount = 0;
        let dueSoonCount = 0;

        tasks.forEach(task => {
            const rawDate = task.due_date || task.deadline;
            const formattedDate = rawDate ? new Date(rawDate).toLocaleDateString("vi-VN") : "---";

            // Tính toán màu highlight cho dòng bài tập
            const highlight = getDeadlineHighlight(task);
            if (highlight.isOverdue) overdueCount++;
            if (highlight.isDueSoon) dueSoonCount++;

            let statusBadgeColor = "bg-secondary";
            if (task.status === "IN_PROGRESS") statusBadgeColor = "bg-warning text-dark";
            if (task.status === "DONE") statusBadgeColor = "bg-success";

            tbody.innerHTML += `
                <tr class="${highlight.rowClass}">
                    <td>${task.id}</td>
                    <td class="fw-bold task-title">${task.title}</td>
                    <td>${task.description || '<span class="text-muted">Không có mô tả</span>'}</td>
                    <td>${formattedDate} ${highlight.deadlineBadge}</td>
                    <td><span class="badge ${statusBadgeColor}">${task.status}</span></td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">Xóa</button>
                    </td>
                </tr>
            `;
        });

        updateWarningBanner(overdueCount, dueSoonCount);
    } catch (err) {
        showAlert("Lỗi tải danh sách bài tập từ máy chủ!", "danger");
    }
}

function resetFilters() {
    document.getElementById("searchInput").value = "";
    document.getElementById("statusFilter").value = "";
    document.getElementById("subjectFilter").value = "";
    fetchTasks();
}

async function deleteTask(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa bài tập này không?")) return;

    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (response.ok || response.status === 204) {
            showAlert("Xóa bài tập thành công!", "success");
            fetchTasks();
        } else {
            const data = await response.json();
            showAlert(data.detail || "Không thể xóa bài tập này!", "danger");
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
    setTimeout(() => alertMsg.classList.add("d-none"), 4000);
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    loadSubjectsForFilter();
    fetchTasks();

    document.getElementById("filterForm").addEventListener("submit", (e) => {
        e.preventDefault();
        fetchTasks();
    });

    document.getElementById("statusFilter").addEventListener("change", fetchTasks);
    document.getElementById("subjectFilter").addEventListener("change", fetchTasks);
    document.getElementById("resetFilterBtn").addEventListener("click", resetFilters);
    document.getElementById("logoutBtn").addEventListener("click", logout);
});