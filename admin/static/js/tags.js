(function(){
  // Estado para modales
  let editingTagId = null;
  let tagToDelete = null;

  function setValuesFromQuery(){
    const qs = new URLSearchParams(window.location.search);
    const setVal = (id, key) => { const el = document.getElementById(id); const val = qs.get(key); if (el && val !== null) el.value = val; };
    setVal('search-input','search');
    setVal('sort-by','sort_by');
    setVal('sort-order','sort_order');
  }

  function clearControls(){
    const ids = ['search-input','sort-by','sort-order'];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (id === 'sort-by') el.value = 'name'; else if (id === 'sort-order') el.value = 'asc'; else el.value = '';
    });
  }

  function collectParams(){
    const params = new URLSearchParams();
    const v = id => { const el = document.getElementById(id); return el ? el.value : ''; };
    const search = v('search-input');
    const sortBy = v('sort-by') || 'name';
    const sortOrder = v('sort-order') || 'asc';
    if (search) params.set('search', search);
    if (sortBy) params.set('sort_by', sortBy);
    if (sortOrder) params.set('sort_order', sortOrder);
    params.set('per_page', (window.TAGS_CONFIG && window.TAGS_CONFIG.perPage) || 25);
    return params;
  }

  function navigateWithParams(page){
    const params = collectParams();
    if (page) params.set('page', page);
    const fragmentUrl = window.TAGS_CONFIG.fragmentUrl + '?' + params.toString();
    const pageUrl = window.TAGS_CONFIG.pageUrl + '?' + params.toString();
    history.replaceState(null, '', pageUrl);
    fetch(fragmentUrl, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text())
      .then(html=>{ const c=document.getElementById('ssr-list-container'); if (c) c.innerHTML = html; })
      .catch(()=>{});
  }

  function setupTagsSSR(){
    setValuesFromQuery();
    const searchInput = document.getElementById('search-input');
    if (searchInput){ let t; searchInput.addEventListener('input', ()=>{ clearTimeout(t); t=setTimeout(()=>{ navigateWithParams(1); }, 300); }); }
    const sortByEl = document.getElementById('sort-by'); if (sortByEl) sortByEl.addEventListener('change', ()=> navigateWithParams(1));
    const sortOrderEl = document.getElementById('sort-order'); if (sortOrderEl) sortOrderEl.addEventListener('change', ()=> navigateWithParams(1));
    const applyBtn = document.getElementById('apply-filters'); if (applyBtn) applyBtn.addEventListener('click', ()=> navigateWithParams(1));
    const clearBtn = document.getElementById('clear-filters'); if (clearBtn) clearBtn.addEventListener('click', ()=>{ clearControls(); navigateWithParams(1); });
    window.changePage = function(page){ navigateWithParams(page); };

    // Form submit crear/editar tag
    const form = document.getElementById('tagForm');
    if (form){ form.addEventListener('submit', handleTagSubmit); }
    const nameInput = document.getElementById('tagName');
    if (nameInput){ nameInput.addEventListener('input', generateSlug); }
  }

  // Modales crear/editar
  function showCreateTagModal(){
    editingTagId = null;
    const t = document.getElementById('tagModalTitle'); if (t) t.textContent = 'Agregar Tag';
    const b = document.getElementById('tagSubmitBtn'); if (b) b.textContent = 'Guardar';
    const f = document.getElementById('tagForm'); if (f) f.reset();
    clearErrors();
    const slug = document.getElementById('tagSlug'); if (slug) slug.value='';
    const m = document.getElementById('tagModal'); if (m) m.classList.remove('hidden');
  }

  function editTag(id, name, slug){
    editingTagId = id;
    const t = document.getElementById('tagModalTitle'); if (t) t.textContent = 'Editar Tag';
    const b = document.getElementById('tagSubmitBtn'); if (b) b.textContent = 'Actualizar';
    const n = document.getElementById('tagName'); if (n) n.value = name || '';
    generateSlug();
    clearErrors();
    const m = document.getElementById('tagModal'); if (m) m.classList.remove('hidden');
  }

  function closeTagModal(){
    const m = document.getElementById('tagModal'); if (m) m.classList.add('hidden');
    editingTagId = null;
  }

  function clearErrors(){
    const e = document.getElementById('tagNameError'); if (e) e.classList.add('hidden');
  }

  function generateSlug(){
    const nameEl = document.getElementById('tagName');
    const slugEl = document.getElementById('tagSlug');
    if (!nameEl || !slugEl) return;
    slugEl.value = (nameEl.value || '').toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }

  async function handleTagSubmit(e){
    e.preventDefault();
    const name = (document.getElementById('tagName')?.value || '').trim();
    if (!name){ const err = document.getElementById('tagNameError'); if (err) err.classList.remove('hidden'); return; }
    try {
      const url = editingTagId ? `/api/tags/${editingTagId}` : '/api/tags';
      const method = editingTagId ? 'PUT' : 'POST';
      const resp = await fetch(url, { method, headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ name }) });
      if (!resp.ok){ const data = await resp.json().catch(()=>({})); throw new Error(data.error || 'Error al guardar el tag'); }
      const wasEditing = !!editingTagId;
      closeTagModal();
      navigateWithParams(1);
      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'success', title: wasEditing ? 'Tag actualizado' : 'Tag creado', text: wasEditing ? 'Actualizado correctamente' : 'Creado correctamente', confirmButtonColor:'#16a34a', timer:2000, showConfirmButton:false });
      }
    } catch(err){
      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'error', title:'Error', text: err.message || 'Error al guardar', confirmButtonColor:'#dc2626' });
      }
    }
  }

  // Modal eliminar
  function showDeleteModal(id, name, sitesCount){
    tagToDelete = id;
    const msg = sitesCount > 0 ? `No se puede eliminar el tag "${name}" porque está asociado a ${sitesCount} sitio(s) histórico(s).` : `¿Estás seguro de que deseas eliminar el tag "${name}"?`;
    const msgEl = document.getElementById('deleteMessage'); if (msgEl) msgEl.textContent = msg;
    const buttons = document.getElementById('deleteModalButtons');
    if (buttons){
      if (sitesCount > 0){
        buttons.innerHTML = `<button onclick="closeDeleteModal()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200">Entendido<\/button>`;
      } else {
        buttons.innerHTML = `
          <button onclick="closeDeleteModal()" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200">Cancelar<\/button>
          <button onclick="deleteTag()" id="confirmDeleteBtn" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition duration-200">Eliminar<\/button>
        `;
      }
    }
    const m = document.getElementById('deleteModal'); if (m) m.classList.remove('hidden');
  }

  function closeDeleteModal(){
    const m = document.getElementById('deleteModal'); if (m) m.classList.add('hidden');
    tagToDelete = null;
  }

  async function deleteTag(){
    if (!tagToDelete) return;
    try{
      const resp = await fetch(`/api/tags/${tagToDelete}`, { method:'DELETE' });
      if (!resp.ok){ const data = await resp.json().catch(()=>({})); throw new Error(data.error || 'Error al eliminar el tag'); }
      closeDeleteModal();
      navigateWithParams(1);
      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'success', title:'Tag eliminado', text:'El tag ha sido eliminado correctamente', confirmButtonColor:'#16a34a', timer:2000, showConfirmButton:false });
      }
    } catch(err){
      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'error', title:'Error', text: err.message || 'Error al eliminar', confirmButtonColor:'#dc2626' });
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    if (!window.TAGS_CONFIG){ window.TAGS_CONFIG = { perPage:25, pageUrl: location.pathname, fragmentUrl: location.pathname + '/fragment' }; }
    setupTagsSSR();
  });

  // Exponer funciones usadas por onclick en el template
  window.showCreateTagModal = showCreateTagModal;
  window.editTag = editTag;
  window.closeTagModal = closeTagModal;
  window.showDeleteModal = showDeleteModal;
  window.closeDeleteModal = closeDeleteModal;
  window.deleteTag = deleteTag;
})();


