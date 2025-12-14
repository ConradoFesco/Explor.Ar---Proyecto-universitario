async function cerrarSesion() {
  try {
    const result = await Swal.fire({
      title: '¿Cerrar sesión?',
      text: '¿Estás seguro de que deseas cerrar sesión?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#dc2626',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Sí, cerrar sesión',
      cancelButtonText: 'Cancelar'
    });
    if (!result.isConfirmed) return;
    Swal.fire({ title: 'Cerrando sesión...', text: 'Redirigiendo...', timer: 600, showConfirmButton: false, didOpen: () => { Swal.showLoading(); } }).then(()=>{ window.location.href = '/logout'; });
  } catch (err){
    console.error('Error al cerrar sesión:', err);
    Swal.fire({ icon:'error', title:'Error', text:'No se pudo cerrar sesión. Intenta nuevamente.', confirmButtonColor:'#dc2626' });
  }
}
window.cerrarSesion = cerrarSesion;

const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const line1 = document.getElementById('line1');
const line2 = document.getElementById('line2');
const line3 = document.getElementById('line3');
let sidebarOpen = false;

function toggleSidebar(){
  sidebarOpen = !sidebarOpen;
  if (sidebarOpen){
    sidebar.classList.remove('-translate-x-full');
    overlay.classList.remove('hidden');
    if (line1 && line2 && line3){
      line1.style.transform = 'rotate(45deg) translate(6px, 6px)';
      line2.style.opacity = '0';
      line3.style.transform = 'rotate(-45deg) translate(6px, -6px)';
    }
  } else {
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
    if (line1 && line2 && line3){
      line1.style.transform = 'none';
      line2.style.opacity = '1';
      line3.style.transform = 'none';
    }
  }
}
if (menuToggle) menuToggle.addEventListener('click', toggleSidebar);
if (overlay) overlay.addEventListener('click', toggleSidebar);

const userMenuToggle = document.getElementById('userMenuToggle');
const userDropdown = document.getElementById('userDropdown');
const userArrow = document.getElementById('userArrow');
let userMenuOpen = false;

function toggleUserMenu(){
  userMenuOpen = !userMenuOpen;
  if (userMenuOpen){
    if (userDropdown) userDropdown.classList.remove('hidden');
    if (userArrow) userArrow.style.transform = 'rotate(180deg)';
  } else {
    if (userDropdown) userDropdown.classList.add('hidden');
    if (userArrow) userArrow.style.transform = 'rotate(0deg)';
  }
}
if (userMenuToggle){
  userMenuToggle.addEventListener('click', e => { e.stopPropagation(); toggleUserMenu(); });
}
document.addEventListener('click', e => {
  if (userMenuOpen && userDropdown && userMenuToggle && !userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)){
    userDropdown.classList.add('hidden');
    if (userArrow) userArrow.style.transform = 'rotate(0deg)';
    userMenuOpen = false;
  }
});

function loadModalContent(url, title, renderFunction, errorFunction = null){
  const modal = document.getElementById('detail-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalContent = document.getElementById('modal-content');
  if (!modal || !modalTitle || !modalContent) return;
  modalTitle.textContent = title;
  modalContent.innerHTML = '<div class="animate-pulse"><div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div><div class="h-4 bg-gray-200 rounded w-1/2"></div></div>';
  modal.classList.remove('hidden');
  fetch(url, { headers: { 'X-Requested-With':'fetch' }})
    .then(response => { if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`); return response.text(); })
    .then(html => { modalContent.innerHTML = typeof renderFunction === 'function' ? renderFunction(html) : html; })
    .catch(error => {
      console.error('Error fetching details:', error);
      modalContent.innerHTML = errorFunction ? errorFunction(error) : `<div class="text-red-600 text-center"><p>Error al cargar los detalles.</p><p class="text-sm mt-2">${error.message}</p></div>`;
    });
}
window.loadModalContent = loadModalContent;

function closeModal(){ const modal = document.getElementById('detail-modal'); if (modal) modal.classList.add('hidden'); }
window.closeModal = closeModal;

document.getElementById('detail-modal')?.addEventListener('click', function(e){ if (e.target === this) closeModal(); });


