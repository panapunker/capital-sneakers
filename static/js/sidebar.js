// Sidebar toggle para móvil y escritorio
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('toggleSidebar');
  const sidebar   = document.getElementById('sidebar');
  const main      = document.getElementById('mainContent');

  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', function () {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
      sidebar.classList.toggle('open');
    } else {
      const collapsed = sidebar.style.width === '60px';
      if (collapsed) {
        sidebar.style.width = '240px';
        main.style.marginLeft = '240px';
        sidebar.querySelectorAll('.nav-label, span').forEach(el => {
          el.style.display = '';
        });
      } else {
        sidebar.style.width = '60px';
        main.style.marginLeft = '60px';
        sidebar.querySelectorAll('.nav-label, span').forEach(el => {
          el.style.display = 'none';
        });
      }
    }
  });

  // Cerrar sidebar en móvil al hacer clic fuera
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    }
  });
});