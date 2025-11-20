// static/js/reviews.js
document.addEventListener('DOMContentLoaded', () => {
  const cfg = window.REVIEWS_CONFIG || {};
  const container = document.getElementById('ssr-list-container');
  let currentPage = 1;
  let currentFilters = {};
  let modalReviewId = null;
  let modalSiteId = null;

  // Helper modal functions (ensure availability and consistent behavior)
  function openModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.remove('hidden');
    // close on backdrop click
    m.addEventListener('click', function onBackdrop(e){ if (e.target === m) { closeModal(id); m.removeEventListener('click', onBackdrop); } });
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add('hidden');
  }
  // expose to global in case other scripts expect them
  window.openModal = openModal;
  window.closeModal = closeModal;

  async function fetchFragment(page = 1, filters = {}) {
    const params = new URLSearchParams();
    params.set('page', page);
    params.set('per_page', cfg.perPage || 25);
    for (const k in filters) {
      // Siempre enviar el filtro 'status', aunque sea vacío
      if (k === 'status') {
        params.set('status', filters[k] ?? '');
      } else if (filters[k] !== '' && filters[k] !== null && filters[k] !== undefined) {
        params.set(k, filters[k]);
      }
    }
    const url = `${cfg.fragmentUrl}?${params.toString()}`;
    const res = await fetch(url, { credentials: 'include', headers: { 'X-Requested-With': 'fetch' } });
    if (!res.ok) {
      const text = await res.text();
      console.error('Error cargando fragmento', res.status, text);
      container.innerHTML = `<div class="text-red-600">Error cargando lista (${res.status})</div>`;
      return;
    }
    const html = await res.text();
    container.innerHTML = html;
    bindButtons();
  }

  // Load review detail fragment and populate modal body
  async function loadReviewDetail(reviewId, siteId) {
    const body = document.getElementById('review-detail-body');
    if (!body) return;
    
    if (!siteId) {
      body.innerHTML = `<div class="text-red-600">Error: site_id requerido</div>`;
      return;
    }

    try {
      const url = `${cfg.detailFragmentUrl}/${reviewId}/fragment?site_id=${siteId}`;
      console.debug('Fetching review detail from', url);
      const res = await fetch(url, { credentials: 'include', headers: { 'X-Requested-With': 'fetch' } });
      
      if (!res.ok) {
        console.debug('Detail fetch failed', res.status);
        body.innerHTML = `<div class="text-red-600">Error cargando detalle (${res.status})</div>`;
        return;
      }
      
      const html = await res.text();
      body.innerHTML = html;
    } catch (err) {
      console.error('Error loading detail', err);
      body.innerHTML = `<div class="text-red-600">Error cargando detalle</div>`;
    }
  }

  function submitForm(action, reviewId, data = {}) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/reviews/${reviewId}/${action}`;
    
    // Agregar campos del formulario
    for (const key in data) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = data[key];
      form.appendChild(input);
    }
    
    // Agregar CSRF token si existe
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrf_token';
      csrfInput.value = csrfToken.getAttribute('content');
      form.appendChild(csrfInput);
    }
    
    document.body.appendChild(form);
    form.submit();
  }

  function bindButtons() {
    // approve
    container.querySelectorAll('.btn-approve').forEach(btn => {
      btn.onclick = () => {
        const id = btn.dataset.id;
        if (confirm('¿Estás seguro que deseas aprobar esta reseña?')) {
          submitForm('aprobar', id);
        }
      };
    });

    // reject (open modal reject section)
    container.querySelectorAll('.btn-reject').forEach(btn => {
      btn.onclick = async () => {
        const id = btn.dataset.id;
        const siteId = btn.dataset.siteId;
        modalReviewId = id;
        modalSiteId = siteId;
        
        // load detail first so body not left in 'Cargando...'
        await loadReviewDetail(id, siteId);
        
        // open modal and show reject UI
        const rejectSection = document.getElementById('reject-section');
        const rejectReason = document.getElementById('rejectReason');
        const rejectMsg = document.getElementById('rejectMsg');
        if (rejectMsg) rejectMsg.classList.add('hidden');
        if (rejectReason) rejectReason.value = '';
        if (rejectSection) rejectSection.classList.remove('hidden');
        // hide other modal action buttons
        document.getElementById('modal-approve')?.classList.add('hidden');
        document.getElementById('modal-delete')?.classList.add('hidden');
        document.getElementById('modal-reject')?.classList.add('hidden');
        document.getElementById('modal-close')?.classList.add('hidden');
        openModal('reviewDetailModal');
      };
    });

    // delete
    container.querySelectorAll('.btn-delete').forEach(btn => {
      btn.onclick = () => {
        const id = btn.dataset.id;
        showDeleteConfirmModal(() => {
          submitForm('eliminar', id);
        });
      };
    });

    // pagination
    container.querySelectorAll('.pagination-btn').forEach(btn => {
      btn.onclick = () => {
        const p = parseInt(btn.dataset.page, 10);
        if (!isNaN(p)) {
          currentPage = p;
          fetchFragment(currentPage, currentFilters);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      };
    });

    // view -> open modal with details
    container.querySelectorAll('.btn-view').forEach(btn => {
      btn.onclick = async () => {
        const id = btn.dataset.id;
        const siteId = btn.dataset.siteId;
        
        try {
          await loadReviewDetail(id, siteId);

          // For 'Ver' the modal should be read-only: hide action buttons and reject section
          const approveBtn = document.getElementById('modal-approve');
          const rejectBtn = document.getElementById('modal-reject');
          const deleteBtn = document.getElementById('modal-delete');
          // hide all action buttons and reject section when opening via 'Ver'
          if (approveBtn) approveBtn.classList.add('hidden');
          if (rejectBtn) rejectBtn.classList.add('hidden');
          if (deleteBtn) deleteBtn.classList.add('hidden');
          document.getElementById('reject-section')?.classList.add('hidden');
          document.getElementById('modal-close')?.classList.remove('hidden');

          // open modal
          openModal('reviewDetailModal');

        } catch (err) {
          console.error('Error loading detail', err);
          alert('Error cargando detalle');
        }
      };
    });
  }

  function gatherFilters(prefix = '') {
    const f = {};
    const searchInput = document.getElementById(prefix + 'search-input');
    // El search_param es 'user' según el template de reviews
    if (searchInput && searchInput.value.trim()) {
      f['user'] = searchInput.value.trim();
    }

    const sortBy = document.getElementById(prefix + 'sort-by');
    if (sortBy && sortBy.value) {
      f.sort_by = sortBy.value;
    } else {
      f.sort_by = 'created_at'; // Valor por defecto
    }
    const sortOrder = document.getElementById(prefix + 'sort-order');
    if (sortOrder && sortOrder.value) {
      f.sort_order = sortOrder.value;
    } else {
      f.sort_order = 'desc'; // Valor por defecto
    }

    // Collect selects and inputs for filters panels by convention: id = filter-<name>
    document.querySelectorAll('[id^="filter-"]').forEach(el => {
      const id = el.id.replace(/^filter-/, '');
      if (el.tagName === 'SELECT') {
        const value = el.value;
        // Mapear rating a rating_from y rating_to
        if (id === 'rating' && value) {
          const rating = parseInt(value, 10);
          if (!isNaN(rating) && rating >= 1 && rating <= 5) {
            f.rating_from = rating;
            f.rating_to = rating;
          }
        } else if (value) {
          f[id] = value;
        }
      } else if (el.type === 'date' || el.type === 'text') {
        if (el.value) {
          f[id] = el.value;
        }
      }
    });

    return f;
  }

  function bindFilterPanel(prefix = '') {
    const applyBtn = document.getElementById(prefix + 'apply-filters');
    const clearBtn = document.getElementById(prefix + 'clear-filters');
    const searchInput = document.getElementById(prefix + 'search-input');
    const sortBy = document.getElementById(prefix + 'sort-by');
    const sortOrder = document.getElementById(prefix + 'sort-order');
    
    // Bind sort changes to trigger search
    if (sortBy) {
      sortBy.addEventListener('change', () => {
        currentFilters = gatherFilters(prefix);
        currentPage = 1;
        fetchFragment(currentPage, currentFilters);
      });
    }
    if (sortOrder) {
      sortOrder.addEventListener('change', () => {
        currentFilters = gatherFilters(prefix);
        currentPage = 1;
        fetchFragment(currentPage, currentFilters);
      });
    }
    
    if (applyBtn) {
      applyBtn.onclick = () => {
        currentFilters = gatherFilters(prefix);
        currentPage = 1;
        // Si el filtro de status es 'Todos' o vacío, no incluir el filtro
        if (currentFilters.status === undefined || currentFilters.status === null || currentFilters.status === '' || currentFilters.status === 'Todos') {
          delete currentFilters.status;
        }
        fetchFragment(currentPage, currentFilters);
      };
    }
    if (clearBtn) {
      clearBtn.onclick = () => {
        // clear inputs inside filters panel
        const panel = document.getElementById(prefix + 'filters-panel');
        if (panel) {
          panel.querySelectorAll('input').forEach(i => i.value = '');
          panel.querySelectorAll('select').forEach(s => s.value = '');
        }
        currentFilters = {};
        currentPage = 1;
        fetchFragment(currentPage, currentFilters);
      };
    }
    // Búsqueda reactiva: al escribir en el input de búsqueda, actualizar resultados
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          currentFilters = gatherFilters(prefix);
          currentPage = 1;
          fetchFragment(currentPage, currentFilters);
        }, 400); // Espera 400ms tras dejar de tipear
      });
    }
  }

  document.addEventListener('filters:apply', (ev) => {
    currentFilters = ev.detail || {};
    currentPage = 1;
    fetchFragment(currentPage, currentFilters);
  });

  // init
  // bind filter panel actions (no prefix was passed when rendering macro in page)
  bindFilterPanel('');
  // initial load: apply existing querystring filters if present
  const initialFilters = {};
  // populate initialFilters from current URL search params (so SSR values persist on first AJAX load)
  const urlParams = new URLSearchParams(window.location.search);
  urlParams.forEach((v,k) => {
    initialFilters[k]=v;
  });
  // Establecer valores de ordenamiento desde URL o por defecto
  if (!initialFilters.sort_by) initialFilters.sort_by = 'created_at';
  if (!initialFilters.sort_order) initialFilters.sort_order = 'desc';
  // No establecer status por defecto (mostrar todas)
  fetchFragment(1, initialFilters);

  // modal reject save/cancel handlers (bind directly - we're already in DOMContentLoaded)
  const saveReject = document.getElementById('saveReject');
  const cancelReject = document.getElementById('cancelReject');
  if (saveReject) {
    saveReject.onclick = () => {
      const reasonEl = document.getElementById('rejectReason');
      const msg = document.getElementById('rejectMsg');
      if (!reasonEl || !msg) return;
      const reason = (reasonEl.value || '').trim();
      if (!reason) { 
        msg.textContent = 'El motivo es obligatorio'; 
        msg.classList.remove('hidden'); 
        return; 
      }
      if (reason.length > 200) { 
        msg.textContent = 'El motivo no puede superar 200 caracteres'; 
        msg.classList.remove('hidden'); 
        return; 
      }
      if (!modalReviewId) { 
        showActionConfirmModal('No hay reseña seleccionada'); 
        return; 
      }
      submitForm('rechazar', modalReviewId, { reason });
    };
  }
  
  // Modal helpers para confirmación de acción y confirmación de borrado
  function showActionConfirmModal(message) {
    const modal = document.getElementById('actionConfirmModal');
    const msgDiv = document.getElementById('action-confirm-message');
    if (msgDiv) msgDiv.textContent = message;
    if (modal) openModal('actionConfirmModal');
  }

  function showDeleteConfirmModal(onConfirm) {
    const modal = document.getElementById('deleteConfirmModal');
    if (!modal) return;
    openModal('deleteConfirmModal');
    const confirmBtn = document.getElementById('confirmDelete');
    const cancelBtn = document.getElementById('cancelDelete');
    // limpiar listeners previos
    confirmBtn.onclick = () => {
      closeModal('deleteConfirmModal');
      if (typeof onConfirm === 'function') onConfirm();
    };
    cancelBtn.onclick = () => {
      closeModal('deleteConfirmModal');
    };
  }
  
  if (cancelReject) { 
    cancelReject.onclick = () => { 
      document.getElementById('reject-section')?.classList.add('hidden'); 
      modalReviewId = null; 
      modalSiteId = null;
      closeModal('reviewDetailModal'); 
    }; 
  }
});
