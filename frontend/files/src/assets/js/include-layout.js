/**
 * Simple HTML include helper. Usage:
 * <div data-include="/layouts/sidebar-pc.html"></div>
 */

(async function() {
  function fetchFragment(url) {
    return fetch(url).then(r => {
      if (!r.ok) throw new Error(`Failed to load ${url}`);
      return r.text();
    });
  }

  // +++ HÀM ĐÃ ĐƯỢC CẬP NHẬT LOGIC +++
  function highlightActiveMenuItem() {
    const currentPath = window.location.pathname;
    const allLinks = document.querySelectorAll('.pc-sidebar .pc-link');

    allLinks.forEach(link => {
      // *** THAY ĐỔI QUAN TRỌNG: Bỏ qua các link chỉ dùng để trigger dropdown ***
      if (link.getAttribute('href') === '#') {
        return; // Chuyển sang xử lý link tiếp theo
      }

      const linkPath = new URL(link.href).pathname;

      if (linkPath === currentPath) {
        // 1. Kích hoạt thẻ <li> chứa link này
        const listItem = link.closest('.pc-item');
        if (listItem) {
          listItem.classList.add('active');
        }

        // 2. Tìm menu cha (nếu có) và kích hoạt nó để mở ra
        const parentMenu = link.closest('.pc-hasmenu');
        if (parentMenu) {
          parentMenu.classList.add('active');
          parentMenu.classList.add('pc-trigger'); // Class này thường dùng để mở menu
        }
      }
    });
  }

  async function loadIncludes() {
    const placeholders = Array.from(document.querySelectorAll('[data-include]'));
    await Promise.all(placeholders.map(async (el) => {
      try {
        const url = el.getAttribute('data-include');
        let html = '';
        try {
          html = await fetchFragment(url);
        } catch (err) {
          const fileName = url.split('/').pop();
          const fallbackUrl = `/layouts/${fileName}`;
          console.warn(`Include failed for ${url}, trying ${fallbackUrl}`);
          html = await fetchFragment(fallbackUrl);
        }
        el.outerHTML = html;
      } catch (err) {
        console.error('Include failed:', err);
      }
    }));

    // Gọi hàm đánh dấu active sau khi include xong
    highlightActiveMenuItem();

    if (typeof add_scroller === 'function') {
      try {
        add_scroller();
      } catch (e) {
        console.warn('add_scroller() failed:', e);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadIncludes);
  } else {
    loadIncludes();
  }
})();