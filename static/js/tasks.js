const API_URL = "http://127.0.0.1:8000/tasks/";
const SUBJECT_API_URL = "http://127.0.0.1:8000/subjects/";
const token = localStorage.getItem("access_token");

let subjectList = [];
let subjectMap = {};

if (!token) {
    window.location.href = "/static/login.html";
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

function formatApiError(data) {
    if (!data || !data.detail) return "Dữ liệu gửi lên chưa hợp lệ!";
    if (Array.isArray(data.detail)) {
        return data.detail.map(e => `${e.loc ? e.loc.slice(-1)[0] : ""}: ${e.msg}`).join(" | ");
    }
    return data.detail;
}

function getOffsetDateString(offsetDays) {
    const d = new Date();
    d.setDate(d.getDate() + offsetDays);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

async function loadSubjects() {
    try {
        const response = await fetch(SUBJECT_API_URL, { headers: getAuthHeaders() });
        if (!response.ok) return;

        const subjects = await response.json();
        if (!Array.isArray(subjects)) return;

        subjectList = subjects;
        subjectMap = {};

        const filterSelect = document.getElementById("subjectFilter");
        const createSelect = document.getElementById("taskSubject");

        filterSelect.innerHTML = `<option value="">-- Tất cả môn học --</option>`;
        createSelect.innerHTML = `<option value="">-- Chọn môn học --</option>`;

        subjects.forEach(sub => {
            const label = `${sub.code} - ${sub.name}`;
            subjectMap[sub.id] = label;
            filterSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
            createSelect.innerHTML += `<option value="${sub.id}">${label}</option>`;
        });
    } catch (err) {
        console.error("Lỗi tải danh sách môn học:", err);
    }
}

function getDeadlineHighlight(task) {
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
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const dueDate = new Date(rawDate);
        dueDate.setHours(0, 0, 0, 0);

        diffDays = Math.round((dueDate - today) / (1000 * 60 * 60 * 24));
    }

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

    return { rowClass: "", deadlineBadge: "", isOverdue: false, isDueSoon: false };
}

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
        const countBadge = document.getElementById("tableTaskCount");
        tbody.innerHTML = "";

        if (!Array.isArray(tasks) || tasks.length === 0) {
            if (countBadge) countBadge.innerText = "0 bài tập";
            updateWarningBanner(0, 0);
            const isFiltering = Boolean(search || status || subjectId);

            if (isFiltering) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                            Không tìm thấy bài tập nào phù hợp với điều kiện lọc.
                        </td>
                    </tr>
                `;
            } else if (subjectList.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5">
                            <p class="text-muted mb-2 fw-bold">Bạn chưa có môn học nào để giao bài tập!</p>
                            <p class="text-muted small mb-3">Hãy tạo môn học trước, sau đó quay lại đây thêm bài tập.</p>
                            <a href="/static/subjects.html" class="btn btn-primary btn-sm">+ Tạo môn học ngay</a>
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5">
                            <p class="text-muted mb-2 fw-bold">Chưa có bài tập nào cho các môn học của bạn!</p>
                            <p class="text-muted small mb-0">Hãy điền thông tin ở khung phía trên hoặc bấm <strong>"✨ Thêm nhanh 4 bài tập mẫu"</strong> trên thanh tiêu đề.</p>
                        </td>
                    </tr>
                `;
            }
            return;
        }

        if (countBadge) countBadge.innerText = `${tasks.length} bài tập`;

        let overdueCount = 0;
        let dueSoonCount = 0;

        tasks.forEach((task, index) => {
            const rawDate = task.due_date || task.deadline;
            const formattedDate = rawDate ? new Date(rawDate).toLocaleDateString("vi-VN") : "---";
            const subjectLabel = subjectMap[task.subject_id] || `Môn #${task.subject_id}`;

            const highlight = getDeadlineHighlight(task);
            if (highlight.isOverdue) overdueCount++;
            if (highlight.isDueSoon) dueSoonCount++;

            tbody.innerHTML += `
                <tr class="${highlight.rowClass}" style="animation-delay: ${index * 0.04}s">
                    <td class="text-muted fw-medium">#${task.id}</td>
                    <td><span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 px-2 py-1">${subjectLabel}</span></td>
                    <td class="fw-bold task-title">${task.title}</td>
                    <td class="text-muted">${task.description || "Không có mô tả"}</td>
                    <td>${formattedDate} ${highlight.deadlineBadge}</td>
                    <td>
                        <select class="form-select form-select-sm" style="width: 145px;" onchange="updateTaskStatus(${task.id}, this.value)">
                            <option value="TODO" ${task.status === "TODO" ? "selected" : ""}>TODO</option>
                            <option value="IN_PROGRESS" ${task.status === "IN_PROGRESS" ? "selected" : ""}>IN_PROGRESS</option>
                            <option value="DONE" ${task.status === "DONE" ? "selected" : ""}>DONE</option>
                        </select>
                    </td>
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

async function createTask(event) {
    event.preventDefault();

    const subjectId = Number(document.getElementById("taskSubject").value);
    const title = document.getElementById("taskTitle").value.trim();
    const dueDate = document.getElementById("taskDueDate").value;
    const status = document.getElementById("taskStatus").value;
    const description = document.getElementById("taskDescription").value.trim();

    if (!subjectId || !title || !dueDate) {
        showAlert("Vui lòng chọn môn học, nhập tiêu đề và chọn hạn chót!", "warning");
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                subject_id: subjectId,
                title: title,
                due_date: dueDate,
                status: status,
                description: description || null
            })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(`Đã thêm bài tập "${title}" thành công!`, "success");
            document.getElementById("createTaskForm").reset();
            fetchTasks();
        } else {
            showAlert(`Không thể thêm bài tập: ${formatApiError(data)}`, "danger");
        }
    } catch (err) {
        showAlert("Lỗi kết nối tới máy chủ FastAPI!", "danger");
    }
}

async function seedSampleTasks() {
    if (subjectList.length === 0) {
        showAlert("Bạn cần tạo ít nhất 1 môn học trước khi thêm bài tập mẫu!", "warning");
        return;
    }

    const s1 = subjectList[0].id;
    const s2 = subjectList[1] ? subjectList[1].id : s1;
    const s3 = subjectList[2] ? subjectList[2].id : s1;
    const s4 = subjectList[3] ? subjectList[3].id : s1;

    const sampleTasks = [
        {
            subject_id: s1,
            title: "Nộp báo cáo phân tích yêu cầu hệ thống",
            description: "Hoàn thành tài liệu đặc tả chức năng và sơ đồ Use Case",
            due_date: getOffsetDateString(-2),
            status: "TODO"
        },
        {
            subject_id: s2,
            title: "Cài đặt thuật toán cây nhị phân tìm kiếm",
            description: "Viết code và chạy bộ kiểm thử các trường hợp biên",
            due_date: getOffsetDateString(1),
            status: "IN_PROGRESS"
        },
        {
            subject_id: s3,
            title: "Thiết kế lược đồ ERD quản lý thư viện",
            description: "Chuẩn hóa dữ liệu đạt chuẩn 3NF và xuất file SQL",
            due_date: getOffsetDateString(6),
            status: "TODO"
        },
        {
            subject_id: s4,
            title: "Tổng hợp dataset huấn luyện mô hình phân loại",
            description: "Làm sạch dữ liệu và chia tập train/test tỷ lệ 80/20",
            due_date: getOffsetDateString(-1),
            status: "DONE"
        }
    ];

    const btn = document.getElementById("seedTasksBtn");
    btn.disabled = true;
    btn.innerText = "Đang tạo...";

    let createdCount = 0;
    let lastError = "";

    for (const item of sampleTasks) {
        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify(item)
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
    btn.innerText = "✨ Thêm nhanh 4 bài tập mẫu";

    if (createdCount > 0) {
        showAlert(`Đã tạo thành công ${createdCount} bài tập mẫu cho các môn học!`, "success");
        fetchTasks();
    } else {
        showAlert(`Không thể tạo bài tập mẫu: ${lastError}`, "danger");
    }
}

async function updateTaskStatus(id, newStatus) {
    try {
        const response = await fetch(`${API_URL}${id}/status`, {
            method: "PATCH",
            headers: getAuthHeaders(),
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            showAlert("Đã cập nhật trạng thái bài tập!", "success");
            fetchTasks();
        } else {
            const data = await response.json();
            showAlert(formatApiError(data), "danger");
        }
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
    setTimeout(() => alertMsg.classList.add("d-none"), 4000);
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadSubjects();
    await fetchTasks();

    document.getElementById("createTaskForm").addEventListener("submit", createTask);
    document.getElementById("seedTasksBtn").addEventListener("click", seedSampleTasks);

    document.getElementById("filterForm").addEventListener("submit", (e) => {
        e.preventDefault();
        fetchTasks();
    });

    document.getElementById("statusFilter").addEventListener("change", fetchTasks);
    document.getElementById("subjectFilter").addEventListener("change", fetchTasks);
    document.getElementById("resetFilterBtn").addEventListener("click", resetFilters);
    document.getElementById("logoutBtn").addEventListener("click", logout);
});