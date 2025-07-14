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

  async function loadIncludes() {
    const placeholders = Array.from(document.querySelectorAll('[data-include]'));
    await Promise.all(placeholders.map(async (el) => {
      try {
        const url = el.getAttribute('data-include');
        let html = '';
        try {
          html = await fetchFragment(url);
        } catch (err) {
          // fallback: try root-relative /layouts/{file}
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

    // Reinitialize PCoded menu if available (sidebar was added after its first run)
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