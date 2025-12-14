(function(){
  function openModal(){ const m=document.getElementById('detail-modal'); if(m) m.classList.remove('hidden'); }
  function setModal(title, html){
    const t=document.getElementById('modal-title'); const c=document.getElementById('modal-content');
    if (t) t.textContent = title;
    if (c) c.innerHTML = html;
  }

  window.openSiteDetail = function(siteId){
    openModal();
    setModal('Detalle del Sitio Histórico','<div class="animate-pulse"><div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div><div class="h-4 bg-gray-200 rounded w-1/2"></div></div>');
    fetch(`/sitios/${siteId}/fragment`, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text()).then(html=> setModal('Detalle del Sitio Histórico', html))
      .catch(()=> setModal('Detalle del Sitio Histórico','<div class="text-red-600 text-center">Error al cargar los detalles.</div>'));
  };

  window.openEditTags = function(siteId){
    openModal();
    setModal('Editar Tags','<div class="animate-pulse"><div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div><div class="h-4 bg-gray-200 rounded w-1/2"></div></div>');
    fetch(`/sitios/${siteId}/tags/fragment`, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text()).then(html=> setModal('Editar Tags', html))
      .catch(()=> setModal('Editar Tags','<div class="text-red-600 text-center">Error al cargar los tags.</div>'));
  };

  window.openEventsHistory = function(siteId, page){
    openModal();
    const modalContent = document.getElementById('modal-content');
    if (modalContent){ modalContent.setAttribute('data-site-id', String(siteId)); window._currentEventsSiteId = siteId; }
    setModal('Historial de Eventos','<div class="animate-pulse"><div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div><div class="h-4 bg-gray-200 rounded w-1/2"></div></div>');
    const panelEl = modalContent.querySelector('#events-filters-panel');
    const filtersOpen = panelEl ? !(panelEl.classList.contains('hidden') || panelEl.style.display === 'none') : false;
    const u = modalContent.querySelector('#events-search-input');
    const t = modalContent.querySelector('#events-filter-type');
    const df = modalContent.querySelector('#events-filter-date-from');
    const dt = modalContent.querySelector('#events-filter-date-to');
    const params = new URLSearchParams();
    if (u && u.value) params.set('user_email', u.value);
    if (t && t.value) params.set('type_action', t.value);
    if (df && df.value) params.set('date_from', df.value);
    if (dt && dt.value) params.set('date_to', dt.value);
    if (page) params.set('page', page);
    params.set('per_page', 10);
    if (typeof window.changePage === 'function' && !window._prevChangePage){ window._prevChangePage = window.changePage; }
    window.changePage = function(p){ updateEventsList(siteId, p); };
    fetch(`/sitios/${siteId}/eventos/fragment` + (params.toString()?`?${params.toString()}`:''), { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text())
      .then(html=>{
        setModal('Historial de Eventos', html);
        attachEventsFiltersListeners(siteId);
        if (filtersOpen){ const p=document.getElementById('events-filters-panel'); if (p){ p.classList.remove('hidden'); p.style.display='block'; } }
      })
      .catch(()=> setModal('Historial de Eventos','<div class="text-red-600 text-center">Error al cargar los eventos.</div>'));
  };

  function buildEventsParams(c, page){
    const u = c.querySelector('#events-search-input');
    const t = c.querySelector('#events-filter-type');
    const df = c.querySelector('#events-filter-date-from');
    const dt = c.querySelector('#events-filter-date-to');
    const params = new URLSearchParams();
    if (u && u.value) params.set('user_email', u.value);
    if (t && t.value) params.set('type_action', t.value);
    if (df && df.value) params.set('date_from', df.value);
    if (dt && dt.value) params.set('date_to', dt.value);
    if (page) params.set('page', page);
    params.set('per_page', 10);
    return params;
  }

  function updateEventsList(siteId, page){
    const c = document.getElementById('modal-content');
    const params = buildEventsParams(c, page);
    const url = `/sitios/${siteId}/eventos/fragment` + (params.toString()?`?${params.toString()}`:'');
    fetch(url, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text())
      .then(html=>{
        const temp = document.createElement('div');
        temp.innerHTML = html;
        const newList = temp.querySelector('#events-list-container');
        const currentList = c.querySelector('#events-list-container');
        if (newList && currentList){ currentList.innerHTML = newList.innerHTML; }
      })
      .catch(()=>{});
  }

  function attachEventsFiltersListeners(siteId){
    const c = document.getElementById('modal-content');
    const search = c.querySelector('#events-search-input');
    if (search){ let t; search.addEventListener('input', ()=>{ clearTimeout(t); t=setTimeout(()=>{ updateEventsList(siteId, 1); }, 300); }); }
    const applyBtn = c.querySelector('#events-apply-filters');
    if (applyBtn){ applyBtn.addEventListener('click', (e)=>{ e.preventDefault(); updateEventsList(siteId, 1); }); }
    const clearBtn = c.querySelector('#events-clear-filters');
    if (clearBtn){ clearBtn.addEventListener('click', (e)=>{ e.preventDefault(); ['events-filter-type','events-filter-date-from','events-filter-date-to','events-search-input'].forEach(id=>{ const el=c.querySelector('#'+id); if(el) el.value=''; }); updateEventsList(siteId, 1); }); }
    const backBtn = Array.from(c.querySelectorAll('button')).find(b=>b.textContent && b.textContent.includes('Volver al detalle'));
    if (backBtn){ backBtn.addEventListener('click', ()=>{ if (window._prevChangePage){ window.changePage = window._prevChangePage; window._prevChangePage = null; } }); }
  }

  document.addEventListener('input', function(e){
    const el = e.target;
    if (el && el.id === 'events-search-input'){
      const btn = document.querySelector('#modal-content [onclick^="openSiteDetail"]');
      const container = document.getElementById('modal-content');
      const idAttr = container ? container.getAttribute('data-site-id') : null;
      const siteId = idAttr ? parseInt(idAttr) : (window._currentEventsSiteId || null);
      if (siteId){ let t; clearTimeout(el._debounceTimer); el._debounceTimer = setTimeout(()=> updateEventsList(siteId, 1), 300); }
    }
  });

  document.addEventListener('click', function(e){
    const t = e.target.closest('#events-apply-filters');
    const c = document.getElementById('modal-content');
    if (t && c){ e.preventDefault(); const idAttr=c.getAttribute('data-site-id'); const siteId = idAttr ? parseInt(idAttr) : (window._currentEventsSiteId || null); if (siteId) updateEventsList(siteId, 1); }
    const clr = e.target.closest('#events-clear-filters');
    if (clr && c){ e.preventDefault(); ['events-filter-type','events-filter-date-from','events-filter-date-to','events-search-input'].forEach(id=>{ const el=c.querySelector('#'+id); if(el) el.value=''; }); const idAttr=c.getAttribute('data-site-id'); const siteId = idAttr ? parseInt(idAttr) : (window._currentEventsSiteId || null); if (siteId) updateEventsList(siteId, 1); }
  });

  window.deleteSite = function(siteId){
    const doSubmit = ()=>{ const f=document.createElement('form'); f.method='POST'; f.action=`/sitios/${siteId}/eliminar`; document.body.appendChild(f); f.submit(); };
    if (typeof Swal !== 'undefined'){
      Swal.fire({ title:'¿Eliminar sitio?', text:'Esta acción no se puede deshacer.', icon:'warning', showCancelButton:true, confirmButtonColor:'#d33', cancelButtonColor:'#6B7280', confirmButtonText:'Sí, eliminar', cancelButtonText:'Cancelar' })
        .then((res)=>{ if(res.isConfirmed){ doSubmit(); } });
    } else { if (confirm('¿Eliminar el sitio?')) doSubmit(); }
  };
})();


