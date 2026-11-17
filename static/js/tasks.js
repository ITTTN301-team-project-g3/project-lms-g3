// Cấu hình Base URL của FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";

// Lấy JWT Token từ localStorage (giả sử lúc đăng nhập đã lưu token ở đây)
function getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// ==========================================
// 1. READ: Lấy và hiển thị danh sách bài tập
// ==========================================
async function fetchTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401) {
                alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
                window.location.href = "/login.html"; // Chuyển về trang login nếu cần
                return;
            }
            throw new Error("Không thể tải danh sách bài tập!");
        }

        const tasks = await response.json();
        renderTaskList(tasks);
    } catch (error) {
        console.error("Lỗi khi tải tasks:", error);
    }
}

// Hàm render danh sách ra giao diện HTML
function renderTaskList(tasks) {
    const taskContainer = document.getElementById("task-list-container");
    if (!taskContainer) return;

    taskContainer.innerHTML = ""; // Xóa nội dung cũ

    if (tasks.length === 0) {
        taskContainer.innerHTML = `<p class="text-gray-500">Chưa có bài tập nào được tạo.</p>`;
        return;
    }

    tasks.forEach(task => {
        const taskCard = document.createElement("div");
        taskCard.className = "p-4 mb-3 border rounded-lg shadow-sm bg-white flex justify-between items-center";
        
        taskCard.innerHTML = `
            <div>
                <h3 class="font-bold text-lg text-gray-800">${escapeHtml(task.title)}</h3>
                <p class="text-gray-600 text-sm">${escapeHtml(task.description || "Không có mô tả")}</p>
                <div class="text-xs text-gray-500 mt-1">
                    <span>Hạn nộp: ${task.due_date ? new Date(task.due_date).toLocaleString() : "Không có"}</span> | 
                    <span class="font-semibold text-blue-600">Trạng thái: ${task.status}</span>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="openEditModal(${task.id}, '${escapeHtml(task.title)}', '${escapeHtml(task.description || '')}', '${task.due_date || ''}', '${task.status}')" 
                    class="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600">Sửa</button>
                <button onclick="deleteTask(${task.id})" 
                    class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600">Xóa</button>
            </div>
        `;
        taskContainer.appendChild(taskCard);
    });
}

// ==========================================
// 2. CREATE: Thêm bài tập mới
// ==========================================
async function handleCreateTask(event) {
    event.preventDefault();

    const title = document.getElementById("task-title").value;
    const description = document.getElementById("task-desc").value;
    const dueDate = document.getElementById("task-duedate").value;
    const statusVal = document.getElementById("task-status").value;
    const subjectId = parseInt(document.getElementById("task-subject-id").value);

    const taskData = {
        title: title,
        description: description,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        status: statusVal,
        subject_id: subjectId
    };

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(taskData)
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Lỗi: ${errData.detail || "Không thể tạo bài tập!"}`);
            return;
        }

        alert("Thêm bài tập thành công!");
        document.getElementById("create-task-form").reset();
        fetchTasks(); // Tải lại danh sách
    } catch (error) {
        console.error("Lỗi khi tạo task:", error);
    }
}

// ==========================================
// 3. UPDATE: Cập nhật bài tập
// ==========================================
async function handleUpdateTask(taskId, updatedData) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify(updatedData)
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Lỗi: ${errData.detail || "Không thể cập nhật bài tập!"}`);
            return;
        }

        alert("Cập nhật bài tập thành công!");
        fetchTasks(); // Tải lại danh sách
    } catch (error) {
        console.error("Lỗi khi cập nhật task:", error);
    }
}

// ==========================================
// 4. DELETE: Xóa bài tập
// ==========================================
async function deleteTask(taskId) {
    if (!confirm("Bạn có chắc chắn muốn xóa bài tập này không?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            alert("Không thể xóa bài tập!");
            return;
        }

        alert("Xóa bài tập thành công!");
        fetchTasks(); // Tải lại danh sách
    } catch (error) {
        console.error("Lỗi khi xóa task:", error);
    }
}

// Hàm hỗ trợ bảo mật chống XSS cơ bản
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// Tự động gọi fetchTasks khi trang được tải xong
document.addEventListener("DOMContentLoaded", () => {
    fetchTasks();
    
    const form = document.getElementById("create-task-form");
    if (form) {
        form.addEventListener("submit", handleCreateTask);
    }
});