document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const alertMessage = document.getElementById('alertMessage');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const fullName = document.getElementById('fullName').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Reset trạng thái thông báo và viền đỏ
        alertMessage.classList.add('d-none');
        alertMessage.classList.remove('alert-danger', 'alert-success');
        document.querySelectorAll('.form-control').forEach(input => input.classList.remove('is-invalid'));

        // Validate cơ bản phía Client
        let isValid = true;
        if (!fullName) {
            document.getElementById('fullName').classList.add('is-invalid');
            isValid = false;
        }
        if (!email || !email.includes('@')) {
            document.getElementById('email').classList.add('is-invalid');
            isValid = false;
        }
        if (!password || password.length < 6) {
            document.getElementById('password').classList.add('is-invalid');
            isValid = false;
        }

        if (!isValid) return;

        // Gọi Backend API Đăng ký
        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Hiển thị thông báo thành công
                alertMessage.classList.remove('d-none');
                alertMessage.classList.add('alert-success');
                alertMessage.innerText = '🎉 Đăng ký thành công! Đang chuyển hướng sang trang đăng nhập...';
                form.reset();

                // Tự động chuyển trang sau 2s
                setTimeout(() => {
                    window.location.href = '/static/login.html';
                }, 2000);
            } else {
                // Hiển thị lỗi từ Backend (vd: Trùng email)
                alertMessage.classList.remove('d-none');
                alertMessage.classList.add('alert-danger');
                alertMessage.innerText = data.detail || 'Đăng ký thất bại. Vui lòng kiểm tra lại!';
            }
        } catch (error) {
            alertMessage.classList.remove('d-none');
            alertMessage.classList.add('alert-danger');
            alertMessage.innerText = 'Không thể kết nối đến server backend!';
        }
    });
});