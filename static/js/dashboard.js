const STATS_API_URL = "/dashboard/stats";
const token = localStorage.getItem("token") || localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/static/login.html";
}

async function loadDashboardStats() {
    try {
        const response = await fetch(STATS_API_URL, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) return;

        const stats = await response.json();

        document.getElementById("totalSubjects").innerText = stats.total_subjects ?? 0;
        document.getElementById("totalTasks").innerText = stats.total_tasks ?? 0;
        document.getElementById("todoTasks").innerText = stats.todo_tasks ?? 0;
        document.getElementById("inProgressTasks").innerText = stats.in_progress_tasks ?? 0;
        document.getElementById("doneTasks").innerText = stats.done_tasks ?? 0;
        document.getElementById("completionRate").innerText = `${stats.completion_rate ?? 0}%`;

        if ((stats.total_tasks ?? 0) === 0) {
            document.getElementById("newAccountBanner").classList.remove("d-none");
        }
    } catch (err) {
        console.error("Lỗi tải thống kê Dashboard:", err);
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