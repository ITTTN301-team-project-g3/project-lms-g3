let allSubjects = [];
let allTasks = [];

function getToken() {
    return localStorage.getItem("token") || localStorage.getItem("access_token");
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getToken()}`
    };
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

function formatErrorDetail(errData, fallback) {
    if (!errData || !errData.detail) return fallback;
    if (typeof errData.detail === "string") return errData.detail;
    if (Array.isArray(errData.detail)) {
        return errData.detail.map(e => e.msg).join(", ");
    }
    return fallback;
}

// 1. Tải danh sách môn học đổ vào dropdown lọc và dropdown trong Modal
async function fetchSubjects() {
    try {
        const response = await fetch("/subjects/", {
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        allSubjects = await response.json();

        const modalSelect = document.getElementById("task-subject-id");
        const filterSelect = document.getElementById("filter-subject");

        modalSelect.innerHTML = `<option value="">-- Chọn môn học --</option>`;
        filterSelect.innerHTML = `<option value="">Tất cả môn học</option>`;

        allSubjects.forEach(sub => {
            const label = `${escapeHtml(sub.code)} - ${escapeHtml(sub.name)}`;
            modalSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
            filterSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
        });
    } catch (error) {
        console.error("Lỗi khi tải danh sách môn học:", error);
    }
}

// 2. Lấy và hiển thị danh sách bài tập
async function fetchTasks() {
    const subjectId = document.getElementById("filter-subject").value;
    const taskStatus = document.getElementById("filter-status").value;

    const params = new URLSearchParams();
    if (subjectId) params.append("subject_id", subjectId);
    if (taskStatus) params.append("task_status", taskStatus);

    const queryString = params.toString() ? `?${params.toString()}` : "";

    try {
        const response = await fetch(`/tasks/${queryString}`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) throw new Error("Không thể tải danh sách bài tập!");

        allTasks = await response.json();
        renderTaskList(allTasks);
    } catch (error) {
        console.error("Lỗi khi tải tasks:", error);
    }
}

function getStatusBadge(status) {
    const styles = {
        "TODO": "bg-gray-200 text-gray-800",
        "IN_PROGRESS": "bg-yellow-100 text-yellow-800",
        "DONE": "bg-green-100 text-green-800"
    };
    return `<span class="px-2 py-0.5 rounded text-xs font-semibold ${styles[status] || "bg-gray-100"}">${status}</span>`;
}

function renderTaskList(tasks) {
    const taskContainer = document.getElementById("task-list-container");
    if (!taskContainer) return;

    taskContainer.innerHTML = "";

    if (tasks.length === 0) {
        taskContainer.innerHTML = `<p class="text-gray-500 text-center py-6">Chưa có bài tập nào phù hợp. Bấm <strong>+ Thêm bài tập</strong> để tạo mới.</p>`;
        return;
    }

    tasks.forEach(task => {
        const subject = allSubjects.find(s => s.id === task.subject_id);
        const subjectLabel = subject ? `${escapeHtml(subject.code)} - ${escapeHtml(subject.name)}` : `Môn #${task.subject_id}`;

        const taskCard = document.createElement("div");
        taskCard.className = "p-4 mb-3 border rounded-lg shadow-sm bg-white flex justify-between items-center hover:border-blue-300 transition";

        taskCard.innerHTML = `
            <div>
                <div class="flex items-center space-x-2 mb-1">
                    <span class="text-xs font-medium px-2 py-0.5 bg-blue-50 text-blue-700 rounded">${subjectLabel}</span>
                    ${getStatusBadge(task.status)}
                </div>
                <h3 class="font-bold text-lg text-gray-800">${escapeHtml(task.title)}</h3>
                <p class="text-gray-600 text-sm">${escapeHtml(task.description || "Không có mô tả")}</p>
                <div class="text-xs text-gray-500 mt-1">
                    Hạn nộp: ${task.due_date ? new Date(task.due_date).toLocaleString("vi-VN") : "Không có"}
                </div>
            </div>
            <div class="flex space-x-2 shrink-0 ml-4">
                <button onclick="openEditModal(${task.id})"
                    class="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600">Sửa</button>
                <button onclick="deleteTask(${task.id})"
                    class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600">Xóa</button>
            </div>
        `;
        taskContainer.appendChild(taskCard);
    });
}

// 3. Mở Modal ở chế độ THÊM MỚI
function openCreateModal() {
    document.getElementById("modal-title").innerText = "Thêm bài tập mới";
    document.getElementById("modal-submit-btn").innerText = "Tạo bài tập";
    document.getElementById("task-form").reset();
    document.getElementById("task-id").value = "";
    document.getElementById("task-status").value = "TODO";

    const modal = document.getElementById("task-modal");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
}

// 4. Mở Modal ở chế độ CHỈNH SỬA
function openEditModal(taskId) {
    const task = allTasks.find(t => t.id === taskId);
    if (!task) return;

    document.getElementById("modal-title").innerText = "Cập nhật bài tập";
    document.getElementById("modal-submit-btn").innerText = "Lưu thay đổi";
    document.getElementById("task-id").value = task.id;
    document.getElementById("task-title").value = task.title;
    document.getElementById("task-desc").value = task.description || "";
    document.getElementById("task-subject-id").value = task.subject_id;
    document.getElementById("task-status").value = task.status;

    if (task.due_date) {
        const dt = new Date(task.due_date);
        const offset = dt.getTimezoneOffset() * 60000;
        document.getElementById("task-duedate").value = new Date(dt - offset).toISOString().slice(0, 16);
    } else {
        document.getElementById("task-duedate").value = "";
    }

    const modal = document.getElementById("task-modal");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
}

function closeTaskModal() {
    const modal = document.getElementById("task-modal");
    modal.classList.add("hidden");
    modal.classList.remove("flex");
}

// 5. Xử lý Submit Form trong Modal (Tự phân biệt POST Thêm mới hoặc PUT Cập nhật)
async function handleSaveTask(event) {
    event.preventDefault();

    const taskId = document.getElementById("task-id").value;
    const dueDate = document.getElementById("task-duedate").value;
    const subjectId = parseInt(document.getElementById("task-subject-id").value);

    if (isNaN(subjectId)) {
        alert("Vui lòng chọn môn học!");
        return;
    }

    const payload = {
        title: document.getElementById("task-title").value.trim(),
        description: document.getElementById("task-desc").value.trim() || null,
        subject_id: subjectId,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        status: document.getElementById("task-status").value
    };

    const method = taskId ? "PUT" : "POST";
    const url = taskId ? `/tasks/${taskId}` : "/tasks/";

    try {
        const response = await fetch(url, {
            method: method,
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Lỗi: ${formatErrorDetail(errData, "Không thể lưu bài tập!")}`);
            return;
        }

        closeTaskModal();
        fetchTasks();
    } catch (error) {
        console.error("Lỗi khi lưu task:", error);
    }
}

// 6. Xóa bài tập
async function deleteTask(taskId) {
    if (!confirm("Bạn có chắc chắn muốn xóa bài tập này không?")) return;

    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Lỗi: ${formatErrorDetail(errData, "Không thể xóa bài tập!")}`);
            return;
        }

        fetchTasks();
    } catch (error) {
        console.error("Lỗi khi xóa task:", error);
    }
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

document.addEventListener("DOMContentLoaded", async () => {
    if (!getToken()) {
        alert("Vui lòng đăng nhập trước!");
        window.location.href = "/static/login.html";
        return;
    }

    await fetchSubjects();
    await fetchTasks();

    document.getElementById("task-form").addEventListener("submit", handleSaveTask);
});

// Cho phép bấm phím ESC để đóng Modal
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeTaskModal();
});