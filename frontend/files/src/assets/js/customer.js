function logoutBtn() {
  Swal.fire({
    title: 'Bạn có chắc chắn muốn đăng xuất không?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Đăng xuất',
    cancelButtonText: 'Huỷ bỏ'
  }).then((result) => {
    if (result.isConfirmed) {
      localStorage.removeItem('access_token');

      Swal.fire({
        icon: 'success',
        title: 'Đã đăng xuất!',
        timer: 1500,
        showConfirmButton: false
      }).then(() => {
        window.location.href = '/'; // hoặc chuyển đến trang login
      });
    }
  });
}

  document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const res = await fetch('https://api.aagents.vn/api/v1/auth/me', {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });

      const data = await res.json();
      if (data?.email && data?.role) {
        document.querySelectorAll('.user_email').forEach(el => el.textContent = data.email);
        document.querySelectorAll('.user_role').forEach(el => el.textContent = data.role);
      }
    } catch (err) {
      console.error('Lỗi khi lấy thông tin người dùng:', err);
    }
  });