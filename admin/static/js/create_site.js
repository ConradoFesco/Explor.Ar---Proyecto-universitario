document.addEventListener('DOMContentLoaded', function(){
  const handleMapClick = function(coords){
    updateFormCoordinates(coords);
    updateMapMarker(coords);
    getLocationInfo(coords);
  };

  if (typeof mapHandler === 'undefined') return;
  mapHandler.initializeMap('map-container', [-34.92, -57.95], 13, handleMapClick);
  mapHandler.loadHistoricSites();

  function updateFormCoordinates(coords){
    const lat = document.getElementById('latitud');
    const lng = document.getElementById('longitud');
    if (lat) lat.value = coords.lat.toFixed(6);
    if (lng) lng.value = coords.lng.toFixed(6);
    if (lat?.value && lng?.value){
      lat.classList.remove('field-error');
      lng.classList.remove('field-error');
      document.getElementById('latitud-error')?.classList.remove('show');
      document.getElementById('longitud-error')?.classList.remove('show');
    }
  }

  function updateMapMarker(coords){
    if (!mapHandler?.map) return;
    if (mapHandler.marker){ mapHandler.marker.setLatLng([coords.lat, coords.lng]); }
    else { mapHandler.marker = L.marker([coords.lat, coords.lng]).addTo(mapHandler.map); }
  }

  function getLocationInfo(coords){
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.lat}&lon=${coords.lng}&zoom=10&addressdetails=1`)
      .then(r=>r.json())
      .then(data=>{
        const cityEl = document.getElementById('ciudad');
        const provEl = document.getElementById('provincia');
        if (data.address){
          const city = data.address.city || data.address.town || data.address.village || data.address.municipality || data.address.suburb || '';
          const prov = data.address.state || data.address.region || data.address.province || '';
          if (cityEl) cityEl.value = city;
          if (provEl) provEl.value = prov;
          if (city && prov) clearLocationErrors();
        } else {
          if (cityEl) cityEl.value = '';
          if (provEl) provEl.value = '';
        }
      })
      .catch(()=>{
        const cityEl = document.getElementById('ciudad');
        const provEl = document.getElementById('provincia');
        if (cityEl) cityEl.value = '';
        if (provEl) provEl.value = '';
      });
  }

  function clearLocationErrors(){
    ['latitud','longitud','ciudad','provincia'].forEach(id=>{
      const el = document.getElementById(id);
      const err = document.getElementById(id+'-error');
      if (el?.value.trim()){
        el.classList.remove('field-error');
        err?.classList.remove('show');
      }
    });
  }

  function loadEstados(){
    const data = (window.SITE_OPTIONS && Array.isArray(window.SITE_OPTIONS.states)) ? window.SITE_OPTIONS.states : [];
    const sel = document.getElementById('estado');
    if (!sel) return;
    sel.innerHTML = '<option value="">Seleccione un estado...</option>';
    data.forEach(e=>{ const o=document.createElement('option'); o.value=e.id; o.textContent=e.state; sel.appendChild(o); });
  }

  function loadCategorias(){
    const data = (window.SITE_OPTIONS && Array.isArray(window.SITE_OPTIONS.categories)) ? window.SITE_OPTIONS.categories : [];
    const sel = document.getElementById('categoria');
    if (!sel) return;
    sel.innerHTML = '<option value="">Seleccione una categoría...</option>';
    data.forEach(c=>{ const o=document.createElement('option'); o.value=c.id; o.textContent=c.name; sel.appendChild(o); });
  }

  window.cancelCreate = function(){
    Swal.fire({ title:'¿Cancelar creación?', text:'¿Estás seguro de que deseas cancelar? Los datos no guardados se perderán.', icon:'warning', showCancelButton:true, confirmButtonColor:'#dc2626', cancelButtonColor:'#6b7280', confirmButtonText:'Sí, cancelar', cancelButtonText:'No, continuar creando' })
      .then(r=>{ if (r.isConfirmed) window.location.href = '/sitios'; });
  };

  window.clearForm = function(){
    const form = document.getElementById('site-form'); if (form) form.reset();
    ['latitud','longitud','ciudad','provincia'].forEach(id=>{ const el=document.getElementById(id); if (el) el.value=''; });
    if (mapHandler?.marker){ mapHandler.map.removeLayer(mapHandler.marker); mapHandler.marker = null; }
    clearFieldErrors();
  };

  function validateRequiredFields(){
    const required = ['nombre','descripcion_breve','estado','categoria','latitud','longitud','ciudad','provincia'];
    let ok = true; clearFieldErrors();
    required.forEach(id=>{ const el=document.getElementById(id); const err=document.getElementById(id+'-error'); if (!el?.value.trim()){ el?.classList.add('field-error'); err?.classList.add('show'); ok=false; } });
    return ok;
  }

  function clearFieldErrors(){
    document.querySelectorAll('.field-error').forEach(el=> el.classList.remove('field-error'));
    document.querySelectorAll('.error-message').forEach(el=> el.classList.remove('show'));
  }

  function showSuccessMessage(){
    Swal.fire({ icon:'success', title:'¡Sitio histórico creado!', text:'El sitio histórico se ha creado exitosamente', confirmButtonColor:'#3B82F6', timer:2000, showConfirmButton:false })
      .then(()=>{ window.location.href = '/sitios'; });
  }

  function handleFormSubmit(e){
    e.preventDefault();
    if (!validateRequiredFields()){
      const first = document.querySelector('.field-error');
      if (first){ first.scrollIntoView({ behavior:'smooth', block:'center' }); first.focus(); }
      return;
    }
    const fd = new FormData(e.target); const data = Object.fromEntries(fd.entries());
    const selectedTags = window.tagSelector ? window.tagSelector.getSelectedTags() : [];
    const payload = {
      name: data.nombre,
      brief_description: data.descripcion_breve,
      complete_description: data.descripcion_completa || null,
      latitude: parseFloat(data.latitud),
      longitude: parseFloat(data.longitud),
      year_inauguration: data.año_inauguración || null,
      id_estado: parseInt(data.estado),
      id_category: parseInt(data.categoria),
      visible: true,
      name_city: data.ciudad,
      name_province: data.provincia,
      tag_ids: selectedTags.map(t=>t.id)
    };
    sendDataToBackend(payload);
  }

  function sendDataToBackend(_data){
    const form = document.getElementById('site-form');
    if (!form) return;
    
    const formData = new FormData(form);
    
    if (_data.tag_ids && Array.isArray(_data.tag_ids)) {
      _data.tag_ids.forEach(tagId => {
        formData.append('tag_ids', tagId);
      });
    }
    
    fetch('/sitios', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(async data => {
      if (data.success) {
        if (data.site_id && typeof imagesManager !== 'undefined') {
          imagesManager.siteId = data.site_id;
          if (imagesManager.pendingImages && imagesManager.pendingImages.length > 0) {
            try {
              await imagesManager.uploadPendingImages(data.site_id);
            } catch (error) {
              console.error('Error al subir imágenes pendientes:', error);
            }
          }
        }
        
        Swal.fire({
          icon: 'success',
          title: '¡Sitio histórico creado!',
          text: data.message || 'El sitio histórico se ha creado exitosamente',
          confirmButtonColor: '#3B82F6',
          timer: 2000,
          showConfirmButton: false
        }).then(() => {
          window.location.href = '/sitios';
        });
      } else {
        showErrorMessage(data.error || 'Error al crear el sitio');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showErrorMessage('Error al crear el sitio: ' + error.message);
    });
  }

  function addNewSiteToMap(site){ if (!mapHandler?.map) return; mapHandler.createSiteMarker(site); mapHandler.centerOnSite(site); }
  function showErrorMessage(msg){ Swal.fire({ icon:'error', title:'Error al crear el sitio', text: msg, confirmButtonColor:'#3B82F6' }); }

  const form = document.getElementById('site-form'); if (form) form.addEventListener('submit', handleFormSubmit);
  loadEstados(); loadCategorias();
  ['nombre','descripcion_breve','estado','categoria','latitud','longitud','ciudad','provincia'].forEach(id=>{
    const el=document.getElementById(id); if (el){ const evt = el.readOnly ? 'change' : 'input'; el.addEventListener(evt, function(){ if (this.value.trim()){ this.classList.remove('field-error'); document.getElementById(id+'-error')?.classList.remove('show'); } }); }
  });

  class TagSelector{
    constructor(containerId){ this.containerId=containerId; this.selectedTags=[]; this.allTags=[]; this.init(); }
    init(){ this.createHTML(); this.loadTags(); }
    createHTML(){ const c=document.getElementById(this.containerId); if (!c) return; c.innerHTML = '<button type="button" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-200" id="open-tag-selector"><i class="bi bi-tags-fill"></i> Agregar Tags</button>'; document.getElementById('open-tag-selector').addEventListener('click', ()=> this.openModal()); }
    async loadTags(){ this.allTags = Array.isArray(window.TAGS_OPTIONS) ? window.TAGS_OPTIONS : []; }
    openModal(){ const modal=document.getElementById('detail-modal'); const title=document.getElementById('modal-title'); const content=document.getElementById('modal-content'); title.textContent='Seleccionar Tags'; content.innerHTML=this.createModalContent(); modal.classList.remove('hidden'); this.bindModalEvents(); }
    createModalContent(){ return `<div class="space-y-4"><div><input type="text" id="tag-search" placeholder="Buscar tags..." class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"></div><div id="tags-container" class="max-h-64 overflow-y-auto space-y-2">${this.renderTagsHTML()}</div><div class="flex justify-end space-x-3 pt-4 border-t border-gray-200"><button type="button" onclick="closeModal()" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200">Cancelar</button><button type="button" id="confirm-tags" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 transition duration-200">Confirmar Selección</button></div></div>`; }
    renderTagsHTML(list=null){ const tags=list||this.allTags; if (!tags.length) return '<div class="text-center text-gray-500 py-4">No se encontraron tags</div>'; return tags.map(tag=>`<div class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition duration-200"><input type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" id="tag-${tag.id}" data-tag-id="${tag.id}" ${this.isSelected(tag.id)?'checked':''}><label for="tag-${tag.id}" class="ml-3 flex-1 cursor-pointer"><span class="font-medium text-gray-900">${tag.name}</span><span class="text-sm text-gray-500 ml-2">(${tag.slug})</span></label></div>`).join(''); }
    bindModalEvents(){ const s=document.getElementById('tag-search'); if (s){ s.addEventListener('input', e=> this.filterTags(e.target.value)); } const c=document.getElementById('confirm-tags'); if (c){ c.addEventListener('click', ()=> this.confirmSelection()); } }
    filterTags(term){ const f=this.allTags.filter(t=> t.name.toLowerCase().includes(term.toLowerCase()) || t.slug.toLowerCase().includes(term.toLowerCase())); const cont=document.getElementById('tags-container'); if (cont){ cont.innerHTML=this.renderTagsHTML(f); this.bindModalEvents(); } }
    isSelected(id){ return this.selectedTags.some(t=> t.id===id); }
    confirmSelection(){ const checks=document.querySelectorAll('#tags-container input[type="checkbox"]:checked'); this.selectedTags=[]; checks.forEach(cb=>{ const id=parseInt(cb.dataset.tagId); const tag=this.allTags.find(t=> t.id===id); if (tag) this.selectedTags.push(tag); }); this.updateSelectedTagsDisplay(); closeModal(); }
    updateSelectedTagsDisplay(){ const btn=document.getElementById('open-tag-selector'); if (!btn) return; btn.innerHTML = this.selectedTags.length>0 ? `<i class="bi bi-tags-fill"></i> Agregar Tags (${this.selectedTags.length} seleccionados)` : `<i class="bi bi-tags-fill"></i> Agregar Tags`; }
    getSelectedTags(){ return [...this.selectedTags]; }
    setSelectedTags(tags){ this.selectedTags=[...tags]; this.updateSelectedTagsDisplay(); }
    clearSelection(){ this.selectedTags=[]; this.updateSelectedTagsDisplay(); }
  }

  if (document.getElementById('tag-selector-container')){ window.tagSelector = new TagSelector('tag-selector-container'); }
  const _origClear = window.clearForm; window.clearForm = function(){ _origClear(); window.tagSelector?.clearSelection(); };
});