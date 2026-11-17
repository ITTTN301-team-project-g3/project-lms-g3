document.addEventListener('DOMContentLoaded', () => {
    // Lắng nghe sự kiện submit của form đăng nhập
    const loginForm = document.querySelector('form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Lấy giá trị email/username và mật khẩu từ ô input
            // (Đảm bảo các input trong file login.html của cậu có đúng dạng hoặc type tương ứng)
            const emailInput = document.querySelector('input[type="email"], input[name="email"], input[id="email"]');
            const passwordInput = document.querySelector('input[type="password"], input[name="password"], input[id="password"]');

            const email = emailInput ? emailInput.value : '';
            const password = passwordInput ? passwordInput.value : '';

            try {
                // Đóng gói dữ liệu gửi lên Backend (FastAPI OAuth2 thường dùng form-urlencoded cho login)
                const formData = new URLSearchParams();
                formData.append('username', email); // FastAPI thường map trường username với email đăng nhập
                formData.append('password', password);

                const response = await fetch('http://127.0.0.1:8000/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Lưu Token vào localStorage của trình duyệt
                    localStorage.setItem('access_token', data.access_token);
                    
                    // Đăng nhập thành công -> Chuyển hướng sang trang quản lý bài tập hoặc dashboard
                    window.location.href = '/static/tasks.html';
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || 'Email hoặc mật khẩu không chính xác!');
                }
            } catch (err) {
                console.error(err);
                alert('Không thể kết nối đến server backend!');
            }
        });
    }
});