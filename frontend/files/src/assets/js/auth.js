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
async function checkRole(allowedRoles = []) {
  const token = localStorage.getItem('access_token');

  try {
    const res = await fetch('https://api.aagents.vn/api/v1/auth/me', {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });

    // if (!res.ok) {
    //   alert('Lỗi xác thực. Vui lòng đăng nhập lại.');
    //   window.location.href = '/pages/auth/login.html';
    //   return false;
    // }

    const user = await res.json();
    const userRole = user.role;

    if (!allowedRoles.includes(userRole)) {
      alert('Bạn không có quyền truy cập trang này.');
      window.history.back(); // quay lại trang trước
      return false;
    }

    return true;

  } catch (error) {
    console.error(error);
    alert('Đã xảy ra lỗi khi kiểm tra quyền truy cập.');
    window.history.back();
    return false;
  }
}

function removeUnauthorizedElements(userRole) {
  const elements = document.querySelectorAll('[data-role-allowed]');

  elements.forEach((el) => {
    const allowedRoles = el.dataset.roleAllowed
      .split(',')
      .map(role => role.trim().toUpperCase());

    if (!allowedRoles.includes(userRole.toUpperCase())) {
      el.remove(); // ❌ Gỡ khỏi DOM luôn
    }
  });
}
async function initAuthRoleCheck() {
  const token = localStorage.getItem('access_token');
  if (!token) return;

  try {
    const res = await fetch('https://api.aagents.vn/api/v1/auth/me', {
      headers: { Authorization: 'Bearer ' + token }
    });

    const user = await res.json();
    removeUnauthorizedElements(user.role);
  } catch (err) {
    console.error('Không thể kiểm tra quyền:', err);
  }
}

document.addEventListener('DOMContentLoaded', initAuthRoleCheck);


