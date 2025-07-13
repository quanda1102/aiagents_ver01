function requireAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    alert('Bạn cần đăng nhập để truy cập trang này!');
    window.location.href = '/'; // Đổi đường dẫn nếu khác
  }
}

function redirectIfAuthenticated() {
  const token = localStorage.getItem('access_token');
  if (token) {
    // Chuyển hướng về trang chính (tuỳ ý, ví dụ: danh sách bài tập)
    window.location.href = '/dashboard/index.html';
  }
}
