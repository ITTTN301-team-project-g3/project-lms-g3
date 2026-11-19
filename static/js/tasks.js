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

        tasks.forEach(task => {
            const rawDate = task.due_date || task.deadline;
            const formattedDate = rawDate ? new Date(rawDate).toLocaleDateString("vi-VN") : "---";

            let badgeColor = "bg-secondary";
            if (task.status === "IN_PROGRESS") badgeColor = "bg-warning text-dark";
            if (task.status === "DONE") badgeColor = "bg-success";

            tbody.innerHTML += `
                <tr>
                    <td>${task.id}</td>
                    <td class="fw-bold">${task.title}</td>
                    <td>${task.description || '<span class="text-muted">Không có mô tả</span>'}</td>
                    <td>${formattedDate}</td>
                    <td><span class="badge ${badgeColor}">${task.status}</span></td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">Xóa</button>
                    </td>
                </tr>
            `;
        });
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