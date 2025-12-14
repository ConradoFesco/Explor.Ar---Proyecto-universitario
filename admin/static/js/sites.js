(function(){
  const cfg = window.SITES_CONFIG || {};
  const perPage = cfg.perPage || 25;

  function v(id){ const el=document.getElementById(id); return el?el.value:''; }

  function collectParams(){
    const params = new URLSearchParams();
    const search = v('search-input');
    const sortBy = v('sort-by') || 'created_at';
    const sortOrder = v('sort-order') || 'desc';
    const cityId = v('filter-city');
    const provinceId = v('filter-province');
    const stateId = v('filter-state');
    const visible = v('filter-visible');
    const dateFrom = v('filter-date-from');
    const dateTo = v('filter-date-to');
    if (search) params.set('search', search.trim());
    if (sortBy) params.set('sort_by', sortBy);
    if (sortOrder) params.set('sort_order', sortOrder);
    if (cityId) params.set('city_id', cityId);
    if (provinceId) params.set('province_id', provinceId);
    if (stateId) params.set('state_id', stateId);
    if (visible !== '') params.set('visible', visible);
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    const tagCheckboxes = document.querySelectorAll('#filter-tag_ids-container input[type="checkbox"]:checked');
    const tagIds = Array.from(tagCheckboxes).map(cb => cb.value).filter(Boolean);
    if (tagIds.length>0) params.set('tag_ids', tagIds.join(','));
    return params;
  }

  function setFromQuery(){
    const qs = new URLSearchParams(window.location.search);
    const setVal=(id,key)=>{ const el=document.getElementById(id); const val=qs.get(key); if(el&&val!==null) el.value=val; };
    setVal('search-input','search');
    setVal('sort-by','sort_by');
    setVal('sort-order','sort_order');
    setVal('filter-city','city_id');
    setVal('filter-province','province_id');
    setVal('filter-state','state_id');
    setVal('filter-visible','visible');
    setVal('filter-date-from','date_from');
    setVal('filter-date-to','date_to');
    const tagParam = qs.get('tag_ids');
    if (tagParam) {
      const ids = tagParam.split(',');
      ids.forEach(id=>{ const cb=document.querySelector(`#filter-tag_ids-container input[type="checkbox"][value="${id}"]`); if(cb) cb.checked=true; });
    }
  }

  function replaceList(params){
    const fragmentUrl = cfg.fragmentUrl + '?' + params.toString();
    const pageUrl = cfg.pageUrl + '?' + params.toString();
    history.replaceState(null, '', pageUrl);
    fetch(fragmentUrl, { headers: { 'X-Requested-With':'fetch' }})
      .then(r=>r.text())
      .then(html=>{ const c=document.getElementById('ssr-list-container'); if(c) c.innerHTML=html; })
      .catch(()=>{});
  }

  function loadFilterOptions(){ }

  function populateOptions(data){
    if (!data) return;
    const addOptions=(sel,items)=>{ if(!sel||!items) return; items.forEach(it=>{ const o=document.createElement('option'); o.value=it.id; o.textContent=it.name; sel.appendChild(o); }); };
    addOptions(document.getElementById('filter-city'), data.cities);
    addOptions(document.getElementById('filter-province'), data.provinces);
    addOptions(document.getElementById('filter-state'), data.states);
    const tagsC = document.getElementById('filter-tags-container');
    if (tagsC && data.tags) {
      data.tags.forEach(tag=>{
        const div=document.createElement('div');
        div.className='flex items-center';
        div.innerHTML=`<input type="checkbox" value="${tag.id}" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"><label class="ml-2 text-sm text-gray-700 cursor-pointer">${tag.name}</label>`;
        tagsC.appendChild(div);
        });
    }
}

  function setup(){
    loadFilterOptions();
    setFromQuery();
    const search = document.getElementById('search-input');
    if (search){ let t; search.addEventListener('input', ()=>{ clearTimeout(t); t=setTimeout(()=>{ const p=collectParams(); p.set('page',1); p.set('per_page', perPage); replaceList(p); }, 300); }); }
    ['sort-by','sort-order'].forEach(id=>{ const el=document.getElementById(id); if(el) el.addEventListener('change', ()=>{ const p=collectParams(); p.set('page',1); p.set('per_page', perPage); replaceList(p); }); });
    const applyBtn=document.getElementById('apply-filters'); if (applyBtn) applyBtn.addEventListener('click', ()=>{ const p=collectParams(); p.set('page',1); p.set('per_page', perPage); replaceList(p); });
    const clearBtn=document.getElementById('clear-filters'); if (clearBtn) clearBtn.addEventListener('click', ()=>{ ['search-input','sort-by','sort-order','filter-city','filter-province','filter-state','filter-visible','filter-date-from','filter-date-to'].forEach(id=>{ const el=document.getElementById(id); if(el) el.value=''; }); document.querySelectorAll('#filter-tag_ids-container input[type="checkbox"]').forEach(cb=>cb.checked=false); const p=collectParams(); p.set('page',1); p.set('per_page', perPage); replaceList(p); });
    window.changePage = function(page){ const p=collectParams(); p.set('page', page); p.set('per_page', perPage); replaceList(p); };
    const exportBtn=document.getElementById('export-btn'); if (exportBtn && cfg.exportCsvUrl){ exportBtn.addEventListener('click', (e)=>{ e.preventDefault(); const p=collectParams(); const url=cfg.exportCsvUrl + '?' + p.toString(); const a=document.createElement('a'); a.href=url; document.body.appendChild(a); a.click(); a.remove(); }); }
  }

  document.addEventListener('DOMContentLoaded', setup);
})();