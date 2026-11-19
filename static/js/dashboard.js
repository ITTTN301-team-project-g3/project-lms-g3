const STATS_API_URL = "/dashboard/stats";
const token = localStorage.getItem("token") || localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/static/login.html";
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

function showAlert(message, type = "danger") {
    const alertMsg = document.getElementById("alertMessage");
    if (!alertMsg) return;
    alertMsg.className = `alert alert-${type} shadow-sm mb-4`;
    alertMsg.innerText = message;
    alertMsg.classList.remove("d-none");
}

async function loadDashboardStats() {
    try {
        const response = await fetch(STATS_API_URL, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            showAlert(data.detail || "Không thể tải dữ liệu thống kê từ máy chủ!");
            return;
        }

        const stats = await response.json();

        document.getElementById("totalSubjects").innerText = stats.total_subjects ?? 0;
        document.getElementById("totalTasks").innerText = stats.total_tasks ?? 0;
        document.getElementById("todoTasks").innerText = stats.todo_tasks ?? 0;
        document.getElementById("inProgressTasks").innerText = stats.in_progress_tasks ?? 0;
        document.getElementById("doneTasks").innerText = stats.done_tasks ?? 0;
        document.getElementById("completionRate").innerText = `${stats.completion_rate ?? 0}%`;

        const banner = document.getElementById("newAccountBanner");
        if (banner) {
            if ((stats.total_tasks ?? 0) === 0) {
                banner.classList.remove("d-none");
            } else {
                banner.classList.add("d-none");
            }
        }
    } catch (err) {
        console.error("Lỗi tải thống kê Dashboard:", err);
        showAlert("Lỗi kết nối máy chủ khi tải thống kê!");
    }
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    loadDashboardStats();
    document.getElementById("logoutBtn").addEventListener("click", logout);
});