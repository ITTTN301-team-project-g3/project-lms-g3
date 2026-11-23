const REGISTER_API_URL = "http://127.0.0.1:8000/auth/register";

function formatRegisterError(data) {
    if (!data || !data.detail) return "Đăng ký thất bại, vui lòng kiểm tra lại thông tin!";
    if (Array.isArray(data.detail)) {
        return data.detail.map(e => `${e.loc ? e.loc.slice(-1)[0] : ""}: ${e.msg}`).join(" | ");
    }
    return data.detail;
}

function playRegisterSuccessTransition(fullName, email) {
    const card = document.getElementById("registerCard");
    const overlay = document.getElementById("registerTransitionOverlay");
    const userPill = document.getElementById("transitionNewUser");

    userPill.innerText = `${fullName} • ${email}`;
    card.classList.add("card-morph-out");

    requestAnimationFrame(() => {
        overlay.classList.add("active");
    });

    setTimeout(() => {
        window.location.href = "/static/login.html";
    }, 1850);
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registerForm");
    const fullNameInput = document.getElementById("fullName");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const togglePasswordBtn = document.getElementById("togglePasswordBtn");
    const submitBtn = document.getElementById("btnSubmit");
    const alertMsg = document.getElementById("alertMessage");

    togglePasswordBtn.addEventListener("click", () => {
        const isPassword = passwordInput.type === "password";
        passwordInput.type = isPassword ? "text" : "password";
        togglePasswordBtn.innerText = isPassword ? "🙈" : "👁️";
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        alertMsg.classList.add("d-none");

        const fullName = fullNameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        let isValid = true;

        if (!fullName) {
            fullNameInput.classList.add("is-invalid");
            isValid = false;
        } else {
            fullNameInput.classList.remove("is-invalid");
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailPattern.test(email)) {
            emailInput.classList.add("is-invalid");
            isValid = false;
        } else {
            emailInput.classList.remove("is-invalid");
        }

        if (!password || password.length < 6) {
            passwordInput.classList.add("is-invalid");
            isValid = false;
        } else {
            passwordInput.classList.remove("is-invalid");
        }

        if (!isValid) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="btn-loading-spinner"></span>Đang khởi tạo tài khoản...';

        try {
            const response = await fetch(REGISTER_API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                playRegisterSuccessTransition(fullName, email);
            } else {
                submitBtn.disabled = false;
                submitBtn.innerText = "Đăng Ký Ngay";
                alertMsg.className = "alert alert-danger mt-2";
                alertMsg.innerText = formatRegisterError(data);
                alertMsg.classList.remove("d-none");
            }
        } catch (err) {
            submitBtn.disabled = false;
            submitBtn.innerText = "Đăng Ký Ngay";
            alertMsg.className = "alert alert-danger mt-2";
            alertMsg.innerText = "Không kết nối được tới máy chủ FastAPI!";
            alertMsg.classList.remove("d-none");
        }
    });
});