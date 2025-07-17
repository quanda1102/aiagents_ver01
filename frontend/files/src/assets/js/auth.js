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

async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return null;
  }

  try {
    const apiUrl = window.getApiUrl ? getApiUrl('ME') : 'https://api.aagents.vn/api/v1/auth/me';
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        window.location.href = '/';
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user info:', error);
    return null;
  }
}

async function checkRole(allowedRoles) {
  const user = await getCurrentUser();
  if (!user) {
    alert('Không thể xác thực người dùng. Vui lòng đăng nhập lại.');
    window.location.href = '/';
    return false;
  }

  if (!allowedRoles.includes(user.role)) {
    alert('Bạn không có quyền truy cập trang này.');
    window.location.href = '/dashboard/index.html';
    return false;
  }

  return true;
}

async function isAdmin() {
  const user = await getCurrentUser();
  return user && user.role === 'ADMIN';
}

// Apply role-based visibility to all elements with data-role-allowed attribute
async function applyRoleBasedVisibility() {
  const user = await getCurrentUser();
  if (!user) return;
  
  const userRole = user.role;
  const elementsWithRoleRestriction = document.querySelectorAll('[data-role-allowed]');
  
  elementsWithRoleRestriction.forEach(element => {
    const allowedRoles = element.getAttribute('data-role-allowed').split(',').map(role => role.trim());
    if (!allowedRoles.includes(userRole)) {
      element.style.display = 'none';
    }
  });
}

// Hide elements from students specifically
async function hideFromStudents() {
  const user = await getCurrentUser();
  if (!user) return;
  
  if (user.role === 'STUDENT') {
    const studentHiddenElements = document.querySelectorAll('[data-hide-from-student]');
    studentHiddenElements.forEach(element => {
      element.style.display = 'none';
    });
  }
}

// Auto-apply role-based visibility when auth.js is loaded
document.addEventListener('DOMContentLoaded', async function() {
  // Wait a bit for other scripts to load
  setTimeout(async () => {
    await applyRoleBasedVisibility();
    await hideFromStudents();
  }, 100);
});
