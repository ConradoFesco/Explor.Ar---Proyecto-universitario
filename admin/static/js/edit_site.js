// Variables globales
let currentSiteId = null;

document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  currentSiteId = urlParams.get('edit');
  if (currentSiteId) { loadSiteData(currentSiteId); } else { showError('No se especificó un sitio para modificar'); }
  setTimeout(() => { initializeMapForEdit(); }, 100);
});

async function loadSiteData(siteId){
  try{
    const resp = await fetch(`/api/historic_sites/${siteId}`);
    if (!resp.ok) throw new Error('Error al cargar los datos del sitio');
    const site = await resp.json();
    setValue('nombre', site.name || '');
    setValue('año_inauguración', site.year_inauguration || '');
    setValue('descripcion_breve', site.brief_description || '');
    setValue('descripcion_completa', site.complete_description || '');
    setValue('latitud', site.latitude || '');
    setValue('longitud', site.longitude || '');
    setValue('ciudad', site.city_name || '');
    setValue('provincia', site.province_name || '');
    const visible = document.getElementById('visible'); if (visible) visible.checked = site.visible === true;
    if (site.latitude && site.longitude){ setMapLocation(parseFloat(site.latitude), parseFloat(site.longitude)); }
    loadStatesAndCategories();
    setTimeout(()=> setSelectedValues(site), 500);
  } catch(err){ console.error('Error:', err); showError('Error al cargar los datos del sitio: ' + err.message); }
}

function initializeMapForEdit(){
  if (typeof mapHandler === 'undefined'){ console.error('mapHandler no disponible'); return; }
  const handleMapClick = function(coords){ updateFormCoordinates(coords); if (mapHandler.map && mapHandler.marker){ mapHandler.marker.setLatLng([coords.lat, coords.lng]); } getLocationInfo(coords); };
  const latInput = document.getElementById('latitud'); const lngInput = document.getElementById('longitud');
  let initial = [-34.92, -57.95];
  if (latInput && lngInput && latInput.value && lngInput.value){ initial = [parseFloat(latInput.value), parseFloat(lngInput.value)]; }
  mapHandler.initializeMap('map-container', initial, 13, handleMapClick);
  if (latInput && lngInput && latInput.value && lngInput.value){ setTimeout(()=> setMapLocation(parseFloat(latInput.value), parseFloat(lngInput.value)), 1000); }
}

function setMapLocation(lat, lng){ setTimeout(()=>{ if (mapHandler && mapHandler.map){ mapHandler.map.setView([lat, lng], 13); if (mapHandler.marker){ mapHandler.marker.setLatLng([lat, lng]); } else { mapHandler.marker = L.marker([lat, lng]).addTo(mapHandler.map); } } }, 500); }

function updateFormCoordinates(coords){ const lat=document.getElementById('latitud'); const lng=document.getElementById('longitud'); if (lat) lat.value = coords.lat.toFixed(6); if (lng) lng.value = coords.lng.toFixed(6); }

function getLocationInfo(coords){ const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.lat}&lon=${coords.lng}&zoom=10&addressdetails=1`; fetch(url).then(r=>r.json()).then(data=>{ const ciudad=document.getElementById('ciudad'); const provincia=document.getElementById('provincia'); if (data.address){ const city = data.address.city || data.address.town || data.address.village || data.address.municipality || data.address.suburb || ''; const prov = data.address.state || data.address.region || data.address.province || ''; if (ciudad) ciudad.value = city; if (provincia) provincia.value = prov; } }).catch(()=>{ const ciudad=document.getElementById('ciudad'); const provincia=document.getElementById('provincia'); if (ciudad) ciudad.value=''; if (provincia) provincia.value=''; }); }

function loadEstados(){ fetch('/api/state_routes').then(r=>r.json()).then(data=>{ const sel=document.getElementById('estado'); if (sel && Array.isArray(data)){ sel.innerHTML = '<option value="">Seleccione un estado...</option>'; data.forEach(e=>{ const opt=document.createElement('option'); opt.value=e.id; opt.textContent=e.state; sel.appendChild(opt); }); } }).catch(()=>{}); }
function loadCategorias(){ fetch('/api/category_routes').then(r=>r.json()).then(data=>{ const sel=document.getElementById('categoria'); if (sel && Array.isArray(data)){ sel.innerHTML = '<option value="">Seleccione una categoría...</option>'; data.forEach(c=>{ const opt=document.createElement('option'); opt.value=c.id; opt.textContent=c.name; sel.appendChild(opt); }); } }).catch(()=>{}); }
function loadStatesAndCategories(){ loadEstados(); loadCategorias(); }
function setSelectedValues(site){ if (site.id_estado){ const sel=document.getElementById('estado'); if (sel) sel.value = site.id_estado; } if (site.id_category){ const sel=document.getElementById('categoria'); if (sel) sel.value = site.id_category; } }

function showError(message){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'error', title:'Error', text: message, confirmButtonColor:'#dc2626' }); } else { alert(message); } }
function showSuccess(message){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'success', title:'¡Éxito!', text: message, confirmButtonColor:'#16a34a', timer:2000, showConfirmButton:false }); } }

document.getElementById('site-form')?.addEventListener('submit', async function(e){
  e.preventDefault();
  if (!validateForm()) return;
  const data = {
    name: document.getElementById('nombre').value,
    year_inauguration: document.getElementById('año_inauguración').value || null,
    brief_description: document.getElementById('descripcion_breve').value,
    complete_description: document.getElementById('descripcion_completa').value || null,
    latitude: parseFloat(document.getElementById('latitud').value),
    longitude: parseFloat(document.getElementById('longitud').value),
    id_ciudad: 1,
    id_estado: parseInt(document.getElementById('estado').value),
    id_category: parseInt(document.getElementById('categoria').value),
    visible: document.getElementById('visible')?.checked === true
  };
  try{
    const resp = await fetch(`/api/historic_sites/${currentSiteId}`, { method:'PUT', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(data) });
    if (resp.ok){ const siteName = document.getElementById('nombre').value || 'el sitio histórico'; if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'success', title:'¡Modificación exitosa!', text:`"${siteName}" ha sido modificado correctamente`, confirmButtonColor:'#16a34a', timer:2000, showConfirmButton:false }).then(()=>{ window.location.href = '/sitios'; }); } else { window.location.href = '/sitios'; } }
    else { const err = await resp.json().catch(()=>({})); if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'error', title:'Error al modificar', text: err.error || 'No se pudo modificar', confirmButtonColor:'#dc2626' }); } }
  } catch(_e){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'error', title:'Error de conexión', text:'No se pudo conectar con el servidor.', confirmButtonColor:'#dc2626' }); } }
});

function validateForm(){
  let ok = true;
  document.querySelectorAll('.error-message').forEach(el => el.classList.add('hidden'));
  const nombre = document.getElementById('nombre').value.trim(); if (!nombre){ document.getElementById('nombre-error').classList.remove('hidden'); ok=false; }
  const desc = document.getElementById('descripcion_breve').value.trim(); if (!desc){ document.getElementById('descripcion_breve-error').classList.remove('hidden'); ok=false; }
  const estado = document.getElementById('estado').value; if (!estado){ document.getElementById('estado-error').classList.remove('hidden'); ok=false; }
  const categoria = document.getElementById('categoria').value; if (!categoria){ document.getElementById('categoria-error').classList.remove('hidden'); ok=false; }
  const lat = document.getElementById('latitud').value; const lng = document.getElementById('longitud').value; if (!lat || !lng){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'warning', title:'Ubicación requerida', text:'Debe seleccionar una ubicación en el mapa haciendo clic en el punto deseado.', confirmButtonColor:'#3B82F6' }); } ok=false; }
  return ok;
}

document.addEventListener('DOMContentLoaded', function(){
  ['nombre','descripcion_breve','estado','categoria'].forEach(id=>{ const el=document.getElementById(id); if (el){ el.addEventListener('input', function(){ this.classList.remove('field-error'); const err=document.getElementById(id+'-error'); if (err){ err.classList.add('hidden'); } }); }});
});


