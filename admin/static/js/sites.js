// Configuración global para sitios
let currentPage = 1;
const perPage = 5;
let filterOptions = null;
let currentFilters = {
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc',
    city_id: '',
    province_id: '',
    tag_ids: [],
    state_id: '',
    date_from: '',
    date_to: '',
    visible: ''
};

// Cargar sitios al inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadFilterOptions();
    loadSites(currentPage);
    setupEventListeners();
});

function setupEventListeners() {
    // Búsqueda
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentFilters.search = e.target.value;
                currentPage = 1;
                loadSites(currentPage);
            }, 500); // Debounce de 500ms
        });
    }

    // Ordenamiento
    const sortBySelect = document.getElementById('sort-by');
    if (sortBySelect) {
        sortBySelect.addEventListener('change', (e) => {
            currentFilters.sort_by = e.target.value;
            currentPage = 1;
            loadSites(currentPage);
        });
    }

    const sortOrderSelect = document.getElementById('sort-order');
    if (sortOrderSelect) {
        sortOrderSelect.addEventListener('change', (e) => {
            currentFilters.sort_order = e.target.value;
            currentPage = 1;
            loadSites(currentPage);
        });
    }

    // Toggle de filtros
    const toggleFiltersBtn = document.getElementById('toggle-filters');
    if (toggleFiltersBtn) {
        toggleFiltersBtn.addEventListener('click', () => {
            const panel = document.getElementById('filters-panel');
            if (panel) {
                panel.classList.toggle('hidden');
            }
        });
    }

    // Filtros
    const filterCity = document.getElementById('filter-city');
    if (filterCity) {
        filterCity.addEventListener('change', (e) => {
            currentFilters.city_id = e.target.value;
        });
    }

    const filterProvince = document.getElementById('filter-province');
    if (filterProvince) {
        filterProvince.addEventListener('change', (e) => {
            currentFilters.province_id = e.target.value;
        });
    }

    const filterState = document.getElementById('filter-state');
    if (filterState) {
        filterState.addEventListener('change', (e) => {
            currentFilters.state_id = e.target.value;
        });
    }

    const filterVisible = document.getElementById('filter-visible');
    if (filterVisible) {
        filterVisible.addEventListener('change', (e) => {
            currentFilters.visible = e.target.value;
        });
    }

    const filterDateFrom = document.getElementById('filter-date-from');
    if (filterDateFrom) {
        filterDateFrom.addEventListener('change', (e) => {
            currentFilters.date_from = e.target.value;
        });
    }

    const filterDateTo = document.getElementById('filter-date-to');
    if (filterDateTo) {
        filterDateTo.addEventListener('change', (e) => {
            currentFilters.date_to = e.target.value;
        });
    }

    // Botones de filtros
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            currentPage = 1;
            loadSites(currentPage);
        });
    }

    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            clearFilters();
        });
    }

    // Botón de exportación CSV
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportSitesToCSV();
        });
    }

    // Modales
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', performDeleteSite);
    }

    const cancelDeleteBtn = document.getElementById('cancelDelete');
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }
}

function loadFilterOptions() {
    fetch('/api/HistoricSite_Routes/filter-options')
        .then(response => response.json())
        .then(data => {
            filterOptions = data;
            populateFilterOptions();
        })
        .catch(error => {
            console.error('Error loading filter options:', error);
        });
}

function populateFilterOptions() {
    if (!filterOptions) return;

    // Poblar ciudades
    const citySelect = document.getElementById('filter-city');
    if (citySelect && filterOptions.cities) {
        filterOptions.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city.id;
            option.textContent = city.name;
            citySelect.appendChild(option);
        });
    }

    // Poblar provincias
    const provinceSelect = document.getElementById('filter-province');
    if (provinceSelect && filterOptions.provinces) {
        filterOptions.provinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province.id;
            option.textContent = province.name;
            provinceSelect.appendChild(option);
        });
    }

    // Poblar estados
    const stateSelect = document.getElementById('filter-state');
    if (stateSelect && filterOptions.states) {
        filterOptions.states.forEach(state => {
            const option = document.createElement('option');
            option.value = state.id;
            option.textContent = state.name;
            stateSelect.appendChild(option);
        });
    }

    // Poblar tags
    const tagsContainer = document.getElementById('tags-filter-container');
    if (tagsContainer && filterOptions.tags) {
        filterOptions.tags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'flex items-center';
            tagElement.innerHTML = `
                <input type="checkbox" id="tag-${tag.id}" value="${tag.id}" 
                       class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="tag-${tag.id}" class="ml-2 text-sm text-gray-700 cursor-pointer">
                    ${tag.name}
                </label>
            `;
            tagsContainer.appendChild(tagElement);

            // Event listener para el checkbox
            const checkbox = tagElement.querySelector('input');
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        if (!currentFilters.tag_ids.includes(tag.id)) {
                            currentFilters.tag_ids.push(tag.id);
                        }
                    } else {
                        currentFilters.tag_ids = currentFilters.tag_ids.filter(id => id !== tag.id);
                    }
                });
            }
        });
    }
}

function clearFilters() {
    currentFilters = {
        search: '',
        sort_by: 'created_at',
        sort_order: 'desc',
        city_id: '',
        province_id: '',
        tag_ids: [],
        state_id: '',
        date_from: '',
        date_to: '',
        visible: ''
    };

    // Limpiar inputs
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';

    const sortBySelect = document.getElementById('sort-by');
    if (sortBySelect) sortBySelect.value = 'created_at';

    const sortOrderSelect = document.getElementById('sort-order');
    if (sortOrderSelect) sortOrderSelect.value = 'desc';

    const filterCity = document.getElementById('filter-city');
    if (filterCity) filterCity.value = '';

    const filterProvince = document.getElementById('filter-province');
    if (filterProvince) filterProvince.value = '';

    const filterState = document.getElementById('filter-state');
    if (filterState) filterState.value = '';

    const filterVisible = document.getElementById('filter-visible');
    if (filterVisible) filterVisible.value = '';

    const filterDateFrom = document.getElementById('filter-date-from');
    if (filterDateFrom) filterDateFrom.value = '';

    const filterDateTo = document.getElementById('filter-date-to');
    if (filterDateTo) filterDateTo.value = '';

    // Limpiar checkboxes de tags
    const tagCheckboxes = document.querySelectorAll('#tags-filter-container input[type="checkbox"]');
    tagCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    currentPage = 1;
    loadSites(currentPage);
}

function buildApiUrl(page) {
    const params = new URLSearchParams({
        page: page,
        per_page: perPage,
        sort_by: currentFilters.sort_by,
        sort_order: currentFilters.sort_order
    });

    if (currentFilters.search) params.append('search', currentFilters.search);
    if (currentFilters.city_id) params.append('city_id', currentFilters.city_id);
    if (currentFilters.province_id) params.append('province_id', currentFilters.province_id);
    if (currentFilters.state_id) params.append('state_id', currentFilters.state_id);
    if (currentFilters.visible !== '') params.append('visible', currentFilters.visible === 'true' ? 'true' : 'false');
    if (currentFilters.date_from) params.append('date_from', currentFilters.date_from);
    if (currentFilters.date_to) params.append('date_to', currentFilters.date_to);
    if (currentFilters.tag_ids.length > 0) params.append('tag_ids', currentFilters.tag_ids.join(','));

    return `/api/HistoricSite_Routes?${params.toString()}`;
}

function loadSites(page) {
    const sitesList = document.getElementById('sites-list');
    const loadingMessage = document.getElementById('loading-message');
    const noSitesMessage = document.getElementById('no-sites-message');
    const paginationControls = document.getElementById('pagination-controls');
    const paginationInfo = document.getElementById('pagination-info');
    const sitesContainer = document.getElementById('sites-container');
    const exportBtn = document.getElementById('export-btn');
    
    // Limpiar contenido anterior
    if (sitesList) sitesList.innerHTML = '';
    if (paginationControls) paginationControls.innerHTML = '';
    if (paginationInfo) paginationInfo.innerHTML = '';
    
    // Mostrar loading
    if (loadingMessage) loadingMessage.classList.remove('hidden');
    if (sitesContainer) sitesContainer.classList.add('hidden');
    if (noSitesMessage) noSitesMessage.classList.add('hidden');
    if (paginationControls) paginationControls.classList.add('hidden');
    if (paginationInfo) paginationInfo.classList.add('hidden');
    if (exportBtn) exportBtn.classList.add('hidden');
    
    const API_URL = buildApiUrl(page);
    
    fetch(API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (loadingMessage) loadingMessage.classList.add('hidden');
            
            if (data.sites.length === 0) {
                if (noSitesMessage) noSitesMessage.classList.remove('hidden');
                if (exportBtn) exportBtn.classList.add('hidden');
                return;
            }
            
            // Mostrar sitios
            if (sitesContainer) sitesContainer.classList.remove('hidden');
            if (exportBtn) exportBtn.classList.remove('hidden');
            
            if (sitesList) {
                data.sites.forEach(site => {
                    const listItem = document.createElement('li');
                    listItem.className = 'py-4 flex justify-between items-center';
                    
                    // Generar badges de tags
                    const tagsHTML = site.tags && site.tags.length > 0 
                        ? `<div class="flex flex-wrap gap-1 mt-2">${site.tags.map(tag => 
                            `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${tag.name}
                            </span>`
                        ).join('')}</div>`
                        : '';
                    
                    // Información adicional del sitio
                    const additionalInfo = [];
                    if (site.city_name) additionalInfo.push(`<span class="text-xs text-gray-500">📍 ${site.city_name}</span>`);
                    if (site.created_at) {
                        const date = new Date(site.created_at);
                        additionalInfo.push(`<span class="text-xs text-gray-500">📅 ${date.toLocaleDateString('es-ES')}</span>`);
                    }
                    if (site.visible !== undefined) {
                        const visibilityIcon = site.visible ? '👁️' : '🚫';
                        additionalInfo.push(`<span class="text-xs text-gray-500">${visibilityIcon} ${site.visible ? 'Visible' : 'No visible'}</span>`);
                    }
                    
                    const additionalInfoHTML = additionalInfo.length > 0 
                        ? `<div class="flex flex-wrap gap-2 mt-1">${additionalInfo.join('')}</div>`
                        : '';
                    
                    listItem.innerHTML = `
                        <div class="flex-1">
                            <span class="text-lg font-medium text-gray-700">${site.name}</span>
                            <p class="text-sm text-gray-500 mt-1">${site.brief_description}</p>
                            ${additionalInfoHTML}
                            ${tagsHTML}
                        </div>
                        <button onclick="viewSiteDetail(${site.id})" 
                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200">
                            Ver Detalle
                        </button>
                    `;
                    sitesList.appendChild(listItem);
                });
            }
            
            // Mostrar controles de paginación
            renderPagination(data.pagination);
            currentPage = page;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            if (loadingMessage) {
                loadingMessage.textContent = 'Error al cargar los datos.';
                loadingMessage.classList.remove('hidden');
            }
            if (sitesContainer) sitesContainer.classList.add('hidden');
            if (exportBtn) exportBtn.classList.add('hidden');
        });
}

function renderPagination(pagination) {
    const paginationControls = document.getElementById('pagination-controls');
    const paginationInfo = document.getElementById('pagination-info');
    
    if (!paginationControls || !paginationInfo) return;
    
    if (pagination.pages <= 1) {
        return; // No mostrar controles si hay solo una página
    }
    
    // Información de paginación
    const startItem = (pagination.page - 1) * pagination.per_page + 1;
    const endItem = Math.min(pagination.page * pagination.per_page, pagination.total);
    paginationInfo.innerHTML = `Mostrando ${startItem}-${endItem} de ${pagination.total} sitios históricos`;
    paginationInfo.classList.remove('hidden');
    
    // Botón Anterior
    const prevButton = document.createElement('button');
    prevButton.innerHTML = '← Anterior';
    prevButton.disabled = !pagination.has_prev;
    prevButton.onclick = () => loadSites(pagination.prev_num);
    prevButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
    paginationControls.appendChild(prevButton);
    
    // Números de página
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    if (startPage > 1) {
        const firstButton = document.createElement('button');
        firstButton.textContent = '1';
        firstButton.onclick = () => loadSites(1);
        firstButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200';
        paginationControls.appendChild(firstButton);
        
        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'px-2 text-gray-500';
            paginationControls.appendChild(ellipsis);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === pagination.page ? 'px-3 py-2 text-sm border border-gray-300 rounded-lg bg-blue-600 text-white border-blue-600 transition duration-200' : 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200';
        pageButton.onclick = () => loadSites(i);
        paginationControls.appendChild(pageButton);
    }
    
    if (endPage < pagination.pages) {
        if (endPage < pagination.pages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'px-2 text-gray-500';
            paginationControls.appendChild(ellipsis);
        }
        
        const lastButton = document.createElement('button');
        lastButton.textContent = pagination.pages;
        lastButton.onclick = () => loadSites(pagination.pages);
        lastButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200';
        paginationControls.appendChild(lastButton);
    }
    
    // Botón Siguiente
    const nextButton = document.createElement('button');
    nextButton.innerHTML = 'Siguiente →';
    nextButton.disabled = !pagination.has_next;
    nextButton.onclick = () => loadSites(pagination.next_num);
    nextButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
    paginationControls.appendChild(nextButton);
    
    paginationControls.classList.remove('hidden');
}

// Funciones específicas para sitios históricos
function viewSiteDetail(siteId) {
    const url = `/api/HistoricSite_Routes/${siteId}`;
    const title = 'Detalle del Sitio Histórico';
    // Usar la función genérica del layout
    if (typeof loadModalContent === 'function') {
        loadModalContent(url, title, renderSiteDetail);
    } else {
        console.error('loadModalContent function not available');
    }
}

// Función específica para renderizar detalles de sitios históricos
function renderSiteDetail(site) {
    return `
        <div class="space-y-6">
            <!-- Información principal -->
            <div class="border-b pb-4">
                <h4 class="text-xl font-bold text-gray-800 mb-2">${site.name}</h4>
                <p class="text-gray-600 leading-relaxed">${site.brief_description}</p>
            </div>
            
            <!-- Descripción completa -->
            ${site.complete_description ? `
                <div>
                    <h5 class="font-semibold text-gray-700 mb-2">Descripción completa</h5>
                    <p class="text-gray-600 leading-relaxed">${site.complete_description}</p>
                </div>
            ` : ''}
            
            <!-- Información geográfica -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-50 p-3 rounded-lg">
                    <h6 class="font-medium text-gray-700 mb-1">Coordenadas</h6>
                    <p class="text-sm text-gray-600">Lat: ${site.latitude}</p>
                    <p class="text-sm text-gray-600">Lng: ${site.longitude}</p>
                </div>
                
                ${site.year_inauguration ? `
                    <div class="bg-gray-50 p-3 rounded-lg">
                        <h6 class="font-medium text-gray-700 mb-1">Año de inauguración</h6>
                        <p class="text-sm text-gray-600">${site.year_inauguration}</p>
                    </div>
                ` : ''}
            </div>
            
            <!-- Tags del sitio -->
            ${site.tags && site.tags.length > 0 ? `
                <div>
                    <h5 class="font-semibold text-gray-700 mb-2">Tags asociados</h5>
                    <div class="flex flex-wrap gap-2">
                        ${site.tags.map(tag => `
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                ${tag.name}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : `
                <div>
                    <h5 class="font-semibold text-gray-700 mb-2">Tags asociados</h5>
                    <p class="text-gray-500 text-sm">Este sitio no tiene tags asociados</p>
                </div>
            `}
            
            <!-- Información de relaciones -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                ${site.city_name ? `
                    <div class="text-center p-2 bg-blue-50 rounded">
                        <span class="font-medium text-blue-700">Ciudad</span>
                        <p class="text-blue-600">${site.city_name}</p>
                    </div>
                ` : ''}
                ${site.state_name ? `
                    <div class="text-center p-2 bg-green-50 rounded">
                        <span class="font-medium text-green-700">Estado</span>
                        <p class="text-green-600">${site.state_name}</p>
                    </div>
                ` : ''}
                ${site.category_name ? `
                    <div class="text-center p-2 bg-purple-50 rounded">
                        <span class="font-medium text-purple-700">Categoría</span>
                        <p class="text-purple-600">${site.category_name}</p>
                    </div>
                ` : ''}
            </div>
            
            <!-- Botones de acción -->
            <div class="flex flex-wrap gap-3 pt-4 border-t border-gray-100 justify-end">
                <button onclick="editSiteTags(${site.id})" 
                        class="group bg-indigo-50 hover:bg-indigo-100 text-indigo-600 border border-indigo-200 hover:border-indigo-300 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:ring-opacity-50">
                    <i class="fas fa-tags mr-2 group-hover:scale-110 transition-transform duration-200"></i>Editar Tags
                </button>
                <button onclick="modifySite(${site.id})" 
                        class="group bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 hover:border-amber-300 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-amber-200 focus:ring-opacity-50">
                    <i class="fas fa-edit mr-2 group-hover:scale-110 transition-transform duration-200"></i>Modificar
                </button>
                <button onclick="deleteSite(${site.id})" 
                        class="group bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 hover:border-red-300 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-red-200 focus:ring-opacity-50">
                    <i class="fas fa-trash mr-2 group-hover:scale-110 transition-transform duration-200"></i>Eliminar
                </button>
                <button onclick="viewEventsHistory(${site.id})" 
                        class="group bg-emerald-50 hover:bg-emerald-100 text-emerald-600 border border-emerald-200 hover:border-emerald-300 font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-emerald-200 focus:ring-opacity-50">
                    <i class="fas fa-history mr-2 group-hover:scale-110 transition-transform duration-200"></i>Historial de Eventos
                </button>
            </div>
        </div>
    `;
}

// Función para modificar un sitio histórico
function modifySite(siteId) {
    // Cerrar el modal actual
    if (typeof closeModal === 'function') {
        closeModal();
    }
    
    // Redirigir a la página de edición
    window.location.href = `/modificar-sitios?edit=${siteId}`;
}

// Función para eliminar un sitio histórico
function deleteSite(siteId) {
    if (confirm('¿Estás seguro de que deseas eliminar este sitio histórico? Esta acción no se puede deshacer.')) {
        const deleteUrl = `/api/HistoricSite_Routes/${siteId}`;
        
        fetch(deleteUrl, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al eliminar el sitio histórico');
            }
            return response.json();
        })
        .then(data => {
            alert('Sitio histórico eliminado correctamente');
            // Cerrar el modal y recargar la lista
            if (typeof closeModal === 'function') {
                closeModal();
            }
            loadSites(currentPage);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el sitio histórico: ' + error.message);
        });
    }
}

function editSiteTags(siteId) {
    // Implementar lógica de edición de tags
    console.log('Editar tags del sitio:', siteId);
}

function viewEventsHistory(siteId) {
    // Implementar lógica de historial de eventos
    console.log('Ver historial de eventos del sitio:', siteId);
}

// Función para exportar sitios a CSV
function exportSitesToCSV() {
    // Construir la URL con los filtros actuales
    const params = new URLSearchParams({
        sort_by: currentFilters.sort_by,
        sort_order: currentFilters.sort_order
    });

    if (currentFilters.search) params.append('search', currentFilters.search);
    if (currentFilters.city_id) params.append('city_id', currentFilters.city_id);
    if (currentFilters.province_id) params.append('province_id', currentFilters.province_id);
    if (currentFilters.state_id) params.append('state_id', currentFilters.state_id);
    if (currentFilters.visible !== '') params.append('visible', currentFilters.visible === 'true' ? 'true' : 'false');
    if (currentFilters.date_from) params.append('date_from', currentFilters.date_from);
    if (currentFilters.date_to) params.append('date_to', currentFilters.date_to);
    if (currentFilters.tag_ids.length > 0) params.append('tag_ids', currentFilters.tag_ids.join(','));

    const exportUrl = `/api/HistoricSite_Routes/export-csv?${params.toString()}`;
    
    // Mostrar indicador de carga
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exportando...';
        exportBtn.disabled = true;
        
        // Crear un enlace temporal para descargar el archivo
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = ''; // El nombre del archivo se establecerá desde el servidor
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Restaurar el botón después de un breve delay
        setTimeout(() => {
            exportBtn.innerHTML = originalText;
            exportBtn.disabled = false;
        }, 2000);
    }
}

// Funciones de modal
function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function performDeleteSite() {
    // Implementar lógica de eliminación
    closeDeleteModal();
}