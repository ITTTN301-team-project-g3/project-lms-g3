const API_URL = "/tasks/";
const SUBJECT_API_URL = "/subjects/";
const token = localStorage.getItem("token") || localStorage.getItem("access_token");

let allSubjects = [];
let allTasks = [];
let taskModalInstance = null;

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

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function loadSubjects() {
    try {
        const response = await fetch(SUBJECT_API_URL, { headers: getAuthHeaders() });
        if (response.status === 401) {
            logout();
            return;
        }
        if (!response.ok) return;

        allSubjects = await response.json();
        const filterSelect = document.getElementById("subjectFilter");
        const modalSelect = document.getElementById("taskSubjectId");

        filterSelect.innerHTML = `<option value="">-- Tất cả môn học --</option>`;
        modalSelect.innerHTML = `<option value="">-- Chọn môn học --</option>`;

        allSubjects.forEach(sub => {
            const label = `${escapeHtml(sub.code)} - ${escapeHtml(sub.name)}`;
            filterSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
            modalSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
        });
    } catch (err) {
        console.error("Lỗi tải danh sách môn học:", err);
    }
}

function renderEmptyState(isFiltering) {
    const emptyState = document.getElementById("emptyState");
    const emptyIcon = document.getElementById("emptyIcon");
    const emptyTitle = document.getElementById("emptyTitle");
    const emptyDesc = document.getElementById("emptyDesc");
    const emptyAction = document.getElementById("emptyAction");

    if (isFiltering) {
        emptyIcon.innerText = "🔍";
        emptyTitle.innerText = "Không tìm thấy bài tập";
        emptyDesc.innerText = "Không có bài tập nào khớp với từ khóa hoặc bộ lọc bạn đã chọn.";
        emptyAction.innerHTML = `<button type="button" class="btn btn-outline-primary" onclick="resetFilters()">Đặt lại bộ lọc</button>`;
    } else if (allSubjects.length === 0) {
        emptyIcon.innerText = "📚";
        emptyTitle.innerText = "Không tìm thấy bài tập";
        emptyDesc.innerText = "Tài khoản của bạn chưa có môn học nào. Hãy tạo môn học trước để thêm bài tập!";
        emptyAction.innerHTML = `<a href="/static/subjects.html" class="btn btn-primary">+ Tạo môn học ngay</a>`;
    } else {
        emptyIcon.innerText = "📭";
        emptyTitle.innerText = "Không tìm thấy bài tập";
        emptyDesc.innerText = "Danh sách bài tập của bạn đang trống. Hãy thêm bài tập mới để theo dõi tiến độ!";
        emptyAction.innerHTML = `<button type="button" class="btn btn-primary" onclick="openCreateModal()">+ Thêm bài tập đầu tiên</button>`;
    }

    emptyState.classList.remove("d-none");
}

async function fetchTasks() {
    const tableWrapper = document.getElementById("tableWrapper");
    const emptyState = document.getElementById("emptyState");
    const tbody = document.getElementById("taskTableBody");

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

        allTasks = await response.json();

        if (!Array.isArray(allTasks) || allTasks.length === 0) {
            tableWrapper.classList.add("d-none");
            renderEmptyState(Boolean(search || status || subjectId));
            return;
        }

        emptyState.classList.add("d-none");
        tableWrapper.classList.remove("d-none");
        tbody.innerHTML = "";

        allTasks.forEach(task => {
            const sub = allSubjects.find(s => s.id === task.subject_id);
            const subBadge = sub ? `<span class="badge bg-info text-dark">${escapeHtml(sub.code)}</span>` : `#${task.subject_id}`;

            const rawDate = task.due_date || task.deadline;
            const formattedDate = rawDate ? new Date(rawDate).toLocaleString("vi-VN") : "---";

            tbody.innerHTML += `
                <tr>
                    <td>${task.id}</td>
                    <td>${subBadge}</td>
                    <td class="fw-bold">${escapeHtml(task.title)}</td>
                    <td>${task.description ? escapeHtml(task.description) : '<span class="text-muted">Không có mô tả</span>'}</td>
                    <td>${formattedDate}</td>
                    <td>
                        <select class="form-select form-select-sm" style="width: 145px;" onchange="quickUpdateStatus(${task.id}, this.value)">
                            <option value="TODO" ${task.status === "TODO" ? "selected" : ""}>TODO</option>
                            <option value="IN_PROGRESS" ${task.status === "IN_PROGRESS" ? "selected" : ""}>IN_PROGRESS</option>
                            <option value="DONE" ${task.status === "DONE" ? "selected" : ""}>DONE</option>
                        </select>
                    </td>
                    <td class="text-center text-nowrap">
                        <button class="btn btn-sm btn-outline-warning me-1" onclick="openEditModal(${task.id})">Sửa</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">Xóa</button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        tableWrapper.classList.add("d-none");
        renderEmptyState(false);
        showAlert("Lỗi tải danh sách bài tập từ máy chủ!", "danger");
    }
}

function openCreateModal() {
    document.getElementById("taskModalLabel").innerText = "Thêm bài tập mới";
    document.getElementById("saveTaskBtn").innerText = "Tạo bài tập";
    document.getElementById("taskForm").reset();
    document.getElementById("taskId").value = "";
    document.getElementById("taskStatus").value = "TODO";
    taskModalInstance.show();
}

function openEditModal(id) {
    const task = allTasks.find(t => t.id === id);
    if (!task) return;

    document.getElementById("taskModalLabel").innerText = "Cập nhật bài tập";
    document.getElementById("saveTaskBtn").innerText = "Lưu thay đổi";
    document.getElementById("taskId").value = task.id;
    document.getElementById("taskTitle").value = task.title;
    document.getElementById("taskDescription").value = task.description || "";
    document.getElementById("taskSubjectId").value = task.subject_id;
    document.getElementById("taskStatus").value = task.status;

    if (task.due_date) {
        const dt = new Date(task.due_date);
        const offset = dt.getTimezoneOffset() * 60000;
        document.getElementById("taskDueDate").value = new Date(dt - offset).toISOString().slice(0, 16);
    } else {
        document.getElementById("taskDueDate").value = "";
    }

    taskModalInstance.show();
}

async function handleSaveTask(e) {
    e.preventDefault();

    const taskId = document.getElementById("taskId").value;
    const dueDateVal = document.getElementById("taskDueDate").value;
    const subjectId = parseInt(document.getElementById("taskSubjectId").value);

    if (isNaN(subjectId)) {
        showAlert("Vui lòng chọn môn học!", "warning");
        return;
    }

    const payload = {
        title: document.getElementById("taskTitle").value.trim(),
        description: document.getElementById("taskDescription").value.trim() || null,
        subject_id: subjectId,
        due_date: dueDateVal ? new Date(dueDateVal).toISOString() : null,
        status: document.getElementById("taskStatus").value
    };

    const method = taskId ? "PUT" : "POST";
    const url = taskId ? `${API_URL}${taskId}` : API_URL;

    try {
        const response = await fetch(url, {
            method: method,
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const data = await response.json();
            const msg = typeof data.detail === "string" ? data.detail : "Không thể lưu bài tập!";
            showAlert(msg, "danger");
            return;
        }

        taskModalInstance.hide();
        showAlert(taskId ? "Cập nhật bài tập thành công!" : "Thêm bài tập mới thành công!", "success");
        fetchTasks();
    } catch (err) {
        showAlert("Lỗi kết nối máy chủ!", "danger");
    }
}

async function quickUpdateStatus(id, newStatus) {
    try {
        const response = await fetch(`${API_URL}${id}/status`, {
            method: "PATCH",
            headers: getAuthHeaders(),
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            showAlert("Không thể cập nhật trạng thái!", "danger");
            fetchTasks();
            return;
        }

        showAlert("Đã cập nhật trạng thái bài tập!", "success");
    } catch (err) {
        showAlert("Lỗi kết nối máy chủ!", "danger");
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
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", async () => {
    taskModalInstance = new bootstrap.Modal(document.getElementById("taskModal"));
    await loadSubjects();
    await fetchTasks();

    document.getElementById("openCreateModalBtn").addEventListener("click", openCreateModal);
    document.getElementById("taskForm").addEventListener("submit", handleSaveTask);
    document.getElementById("filterForm").addEventListener("submit", (e) => {
        e.preventDefault();
        fetchTasks();
    });
    document.getElementById("statusFilter").addEventListener("change", fetchTasks);
    document.getElementById("subjectFilter").addEventListener("change", fetchTasks);
    document.getElementById("resetFilterBtn").addEventListener("click", resetFilters);
    document.getElementById("logoutBtn").addEventListener("click", logout);
});