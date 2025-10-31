(function(){
  function setFiltersFromQuery(){
    const qs = new URLSearchParams(window.location.search);
    const setVal = (id, key) => { const el = document.getElementById(id); const val = qs.get(key); if (el && val !== null) el.value = val; };
    setVal('search-input','search');
    setVal('sort-by','sort_by');
    setVal('sort-order','sort_order');
    setVal('filter-activo','activo');
    setVal('filter-rol','rol');
  }

  function clearFiltersControls(){
    const ids = ['search-input','sort-by','sort-order','filter-activo','filter-rol'];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (id === 'sort-by') el.value = 'created_at'; else if (id === 'sort-order') el.value = 'desc'; else el.value = '';
    });
  }

  function collectParamsFromControls(){
    const params = new URLSearchParams();
    const v = (id) => { const el = document.getElementById(id); return el ? el.value : ''; };
    const search = v('search-input');
    const sortBy = v('sort-by') || 'created_at';
    const sortOrder = v('sort-order') || 'desc';
    const activo = v('filter-activo');
    const rol = v('filter-rol');
    if (search) params.set('search', search);
    if (sortBy) params.set('sort_by', sortBy);
    if (sortOrder) params.set('sort_order', sortOrder);
    if (activo) params.set('activo', activo);
    if (rol) params.set('rol', rol);
    return params;
  }

  function navigateWithParams(page){
    const params = collectParamsFromControls();
    if (page) params.set('page', page);
    params.set('per_page', 25);
    const fragmentUrl = window.USERS_CONFIG.fragmentUrl + '?' + params.toString();
    const pageUrl = window.USERS_CONFIG.pageUrl + '?' + params.toString();
    history.replaceState(null, '', pageUrl);
    fetch(fragmentUrl, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text())
      .then(html=>{ const c=document.getElementById('ssr-list-container'); if (c) c.innerHTML = html; })
      .catch(()=>{});
  }

  function setupUsersSSRListeners(){
    setFiltersFromQuery();
    const searchInput = document.getElementById('search-input');
    if (searchInput){ let t; searchInput.addEventListener('input', ()=>{ clearTimeout(t); t=setTimeout(()=>{ navigateWithParams(1); }, 300); }); }
    const sortByEl = document.getElementById('sort-by'); if (sortByEl) sortByEl.addEventListener('change', ()=> navigateWithParams(1));
    const sortOrderEl = document.getElementById('sort-order'); if (sortOrderEl) sortOrderEl.addEventListener('change', ()=> navigateWithParams(1));
    const applyBtn = document.getElementById('apply-filters'); if (applyBtn) applyBtn.addEventListener('click', ()=> navigateWithParams(1));
    const clearBtn = document.getElementById('clear-filters'); if (clearBtn) clearBtn.addEventListener('click', ()=>{ clearFiltersControls(); navigateWithParams(1); });
    // Toggle del panel lo maneja el onclick inline del macro (evita doble toggle)
    // Delegación para mantener funcional tras re-render del fragmento
    document.addEventListener('click', (e)=>{
      const t = e.target;
      if (t && t.id === 'apply-filters'){ e.preventDefault(); navigateWithParams(1); }
      if (t && t.id === 'clear-filters'){ e.preventDefault(); clearFiltersControls(); navigateWithParams(1); }
      // no delegated toggle handler to avoid double toggle with inline onclick
    });
    // Paginador
    window.changePage = function(page){ navigateWithParams(page); };

    // Delegación para eliminar usuario
    document.addEventListener('click', function(e){
      const btn = e.target.closest('.js-delete-user');
      if (!btn) return;
      e.preventDefault();
      const userId = btn.getAttribute('data-user-id');
      const userName = btn.getAttribute('data-user-name') || '';
      if (!userId) return;
      if (typeof Swal === 'undefined') return;
      Swal.fire({ title:'¿Eliminar usuario?', text:`¿Estás seguro de eliminar a ${userName}? Esta acción no se puede deshacer.`, icon:'warning', showCancelButton:true, confirmButtonColor:'#dc2626', cancelButtonColor:'#6b7280', confirmButtonText:'Sí, eliminar', cancelButtonText:'Cancelar' }).then((result)=>{
        if (!result.isConfirmed) return;
        const form = document.createElement('form'); form.method='POST'; form.action = `/users/${userId}/eliminar`;
        const reason = document.createElement('input'); reason.type='hidden'; reason.name='reason'; reason.value='';
        form.appendChild(reason); document.body.appendChild(form); form.submit();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    if (!window.USERS_CONFIG){ window.USERS_CONFIG = { perPage:25, pageUrl: location.pathname, fragmentUrl: location.pathname + '/fragment' }; }
    setupUsersSSRListeners();
  });
})();


