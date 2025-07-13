  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    if (confirm('Bạn có chắc chắn muốn đăng xuất không?')) {
      localStorage.removeItem('access_token');
      alert('Đã đăng xuất!');
      window.location.href = '/'; // hoặc về trang chủ
    }
  });