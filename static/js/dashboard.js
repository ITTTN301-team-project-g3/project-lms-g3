const STATS_API_URL = "http://127.0.0.1:8000/dashboard/stats";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/static/login.html";
}

function setFormattedDate() {
    const badge = document.getElementById("currentDateBadge");
    if (!badge) return;
    const now = new Date();
    const formatted = now.toLocaleDateString("vi-VN", {
        weekday: "long",
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
    badge.innerText = `📅 ${formatted.charAt(0).toUpperCase() + formatted.slice(1)}`;
}

function showAlert(message, type) {
    const alertMsg = document.getElementById("alertMessage");
    alertMsg.className = `alert alert-${type}`;
    alertMsg.innerText = message;
    alertMsg.classList.remove("d-none");
}

function animateCounter(elementId, targetValue, suffix = "") {
    const el = document.getElementById(elementId);
    if (!el) return;

    const end = Number(targetValue) || 0;
    if (end === 0) {
        el.innerText = `0${suffix}`;
        return;
    }

    const duration = 700;
    const startTime = performance.now();
    const isDecimal = !Number.isInteger(end);

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = end * eased;

        el.innerText = isDecimal
            ? `${current.toFixed(1)}${suffix}`
            : `${Math.round(current)}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            el.innerText = `${end}${suffix}`;
        }
    }

    requestAnimationFrame(step);
}

function updateVisualBars(stats) {
    const total = Number(stats.total_tasks) || 0;
    const todo = Number(stats.todo_tasks) || 0;
    const inProgress = Number(stats.in_progress_tasks) || 0;
    const done = Number(stats.done_tasks) || 0;
    const rate = Math.min(100, Math.max(0, Number(stats.completion_rate) || 0));

    const heroBar = document.getElementById("heroProgressBar");
    const heroText = document.getElementById("heroProgressText");
    const heroNote = document.getElementById("heroSummaryNote");

    if (heroBar) heroBar.style.width = `${rate}%`;
    if (heroText) heroText.innerText = `${rate}%`;
    if (heroNote) {
        heroNote.innerText = total > 0
            ? `Đã hoàn thành ${done}/${total} bài tập trên tổng số ${stats.total_subjects ?? 0} môn học`
            : "Chưa có dữ liệu bài tập để tính tiến độ";
    }

    const todoPct = total > 0 ? Math.round((todo / total) * 100) : 0;
    const progressPct = total > 0 ? Math.round((inProgress / total) * 100) : 0;
    const donePct = total > 0 ? Math.max(0, 100 - todoPct - progressPct) : 0;

    document.getElementById("pctTodo").innerText = `${todoPct}%`;
    document.getElementById("pctInProgress").innerText = `${progressPct}%`;
    document.getElementById("pctDone").innerText = `${donePct}%`;

    requestAnimationFrame(() => {
        document.getElementById("barTodo").style.width = `${todoPct}%`;
        document.getElementById("barInProgress").style.width = `${progressPct}%`;
        document.getElementById("barDone").style.width = `${donePct}%`;
    });
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

        const stats = await response.json();

        if (!response.ok) {
            showAlert(stats.detail || `Không tải được dữ liệu thống kê (${response.status})`, "danger");
            return;
        }

        animateCounter("totalSubjects", stats.total_subjects ?? 0);
        animateCounter("totalTasks", stats.total_tasks ?? 0);
        animateCounter("todoTasks", stats.todo_tasks ?? 0);
        animateCounter("inProgressTasks", stats.in_progress_tasks ?? 0);
        animateCounter("doneTasks", stats.done_tasks ?? 0);
        animateCounter("completionRate", stats.completion_rate ?? 0, "%");

        updateVisualBars(stats);

        if ((stats.total_tasks ?? 0) === 0) {
            document.getElementById("newAccountBanner").classList.remove("d-none");
        }
    } catch (err) {
        showAlert("Chưa kết nối được tới máy chủ FastAPI (127.0.0.1:8000). Hãy bật server trước khi test!", "danger");
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/static/login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    setFormattedDate();
    loadDashboardStats();
    document.getElementById("logoutBtn").addEventListener("click", logout);
});