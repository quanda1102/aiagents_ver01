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
    if (data) {
      // Role: English -> Vietnamese
      const roleMap = {
        ADMIN: "Quản trị viên",
        TEACHER: "Giáo viên",
        STUDENT: "Học sinh"
      };
      const roleVi = roleMap[data.role] || data.role;

      // Gender: English -> Vietnamese + Icon
      const genderMap = {
        male: { label: "Nam", icon: "ti ti-mars" },
        female: { label: "Nữ", icon: "ti ti-venus" }
      };
      const genderInfo = genderMap[data.gender] || { label: "Không rõ", icon: "ti ti-help" };

      document.querySelectorAll('.user_email').forEach(el => el.textContent = data.email);
      document.querySelectorAll('.user_name').forEach(el => el.textContent = data.full_name);
      document.querySelectorAll('.user_age').forEach(el => el.textContent = data.age);
      document.querySelectorAll('.user_role').forEach(el => el.textContent = roleVi);
      document.querySelectorAll('.user_gender').forEach(el => el.textContent = genderInfo.label);

      // Đổi icon giới tính
      const genderIcon = document.querySelector('.ti-map-pin');
      if (genderIcon) {
        genderIcon.className = genderInfo.icon; // Gán class mới
      }
    }
  } catch (err) {
    console.error('Lỗi khi lấy thông tin người dùng:', err);
  }
});