/**
 * Funcionalidades comunes reutilizables para la aplicación
 */

// ===== FUNCIONES DE PAGINACIÓN =====
function changePage(page) {
    if (typeof loadData === 'function') {
        loadData(page);
    } else {
        console.warn('loadData function not defined');
    }
}

// ===== FUNCIONES DE MODAL =====
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Cerrar modal al hacer clic fuera de él
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('backdrop-blur-sm')) {
        const modal = e.target.closest('[id$="-modal"]');
        if (modal) {
            closeModal(modal.id);
        }
    }
});

// ===== FUNCIONES DE FILTROS =====
class FilterManager {
    constructor(config) {
        this.config = config;
        this.currentFilters = {};
        this.currentPage = 1;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Búsqueda con debounce
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.currentFilters.search = e.target.value;
                    this.currentPage = 1;
                    this.applyFilters();
                }, 500);
            });
        }

        // Ordenamiento
        const sortBy = document.getElementById('sort-by');
        const sortOrder = document.getElementById('sort-order');
        
        if (sortBy) {
            sortBy.addEventListener('change', (e) => {
                this.currentFilters.sort_by = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        if (sortOrder) {
            sortOrder.addEventListener('change', (e) => {
                this.currentFilters.sort_order = e.target.value;
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        // Toggle de filtros
        const toggleFilters = document.getElementById('toggle-filters');
        if (toggleFilters) {
            toggleFilters.addEventListener('click', () => {
                const panel = document.getElementById('filters-panel');
                if (panel) {
                    panel.classList.toggle('hidden');
                }
            });
        }

        // Filtros específicos
        this.config.filters?.forEach(filter => {
            const element = document.getElementById(`filter-${filter.name}`);
            if (element) {
                element.addEventListener('change', () => {
                    this.currentFilters[filter.name] = element.value;
                });
            }
        });

        // Botones de filtros
        const applyFilters = document.getElementById('apply-filters');
        const clearFilters = document.getElementById('clear-filters');

        if (applyFilters) {
            applyFilters.addEventListener('click', () => {
                this.currentPage = 1;
                this.applyFilters();
            });
        }

        if (clearFilters) {
            clearFilters.addEventListener('click', () => {
                this.clearFilters();
            });
        }
    }

    applyFilters() {
        if (typeof loadData === 'function') {
            loadData(this.currentPage, this.currentFilters);
        }
    }

    clearFilters() {
        this.currentFilters = {
            search: '',
            sort_by: this.config.defaultSortBy || 'created_at',
            sort_order: this.config.defaultSortOrder || 'desc'
        };

        // Limpiar inputs
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';

        const sortBy = document.getElementById('sort-by');
        if (sortBy) sortBy.value = this.currentFilters.sort_by;

        const sortOrder = document.getElementById('sort-order');
        if (sortOrder) sortOrder.value = this.currentFilters.sort_order;

        // Limpiar filtros específicos
        this.config.filters?.forEach(filter => {
            const element = document.getElementById(`filter-${filter.name}`);
            if (element) {
                element.value = '';
            }
        });

        this.currentPage = 1;
        this.applyFilters();
    }

    buildApiUrl(page, baseUrl) {
        const params = new URLSearchParams({
            page: page,
            per_page: this.config.perPage || 25,
            sort_by: this.currentFilters.sort_by || this.config.defaultSortBy || 'created_at',
            sort_order: this.currentFilters.sort_order || this.config.defaultSortOrder || 'desc'
        });

        // Agregar filtros activos
        Object.entries(this.currentFilters).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        return `${baseUrl}?${params.toString()}`;
    }
}

// ===== FUNCIONES DE TABLA =====
class DataTableManager {
    constructor(config) {
        this.config = config;
        this.currentPage = 1;
        this.currentFilters = {};
    }

    showLoading(show = true) {
        const loadingMessage = document.getElementById('loading-message');
        const dataContainer = document.getElementById('data-container');
        const noDataMessage = document.getElementById('no-data-message');

        if (show) {
            if (loadingMessage) loadingMessage.classList.remove('hidden');
            if (dataContainer) dataContainer.classList.add('hidden');
            if (noDataMessage) noDataMessage.classList.add('hidden');
        } else {
            if (loadingMessage) loadingMessage.classList.add('hidden');
        }
    }

    showData(data) {
        const dataContainer = document.getElementById('data-container');
        const noDataMessage = document.getElementById('no-data-message');

        if (data.length === 0) {
            if (dataContainer) dataContainer.classList.add('hidden');
            if (noDataMessage) noDataMessage.classList.remove('hidden');
        } else {
            if (dataContainer) dataContainer.classList.remove('hidden');
            if (noDataMessage) noDataMessage.classList.add('hidden');
            this.renderData(data);
        }
    }

    renderData(data) {
        if (this.config.type === 'table') {
            this.renderTable(data);
        } else if (this.config.type === 'list') {
            this.renderList(data);
        }
    }

    renderTable(data) {
        const tbody = document.getElementById('data-table-body');
        if (!tbody) return;

        tbody.innerHTML = data.map(item => {
            let row = '<tr class="hover:bg-gray-50">';
            
            this.config.columns.forEach(column => {
                row += '<td class="px-6 py-4 whitespace-nowrap">';
                
                if (column.type === 'text') {
                    row += `<div class="text-sm font-medium text-gray-900">${item[column.field] || '-'}</div>`;
                } else if (column.type === 'badge') {
                    const badgeClass = column.badge_class || 'bg-blue-100 text-blue-800';
                    row += `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeClass}">${item[column.field] || '-'}</span>`;
                } else if (column.type === 'date') {
                    const date = item[column.field] ? new Date(item[column.field]).toLocaleDateString() : '-';
                    row += `<div class="text-sm text-gray-500">${date}</div>`;
                } else {
                    row += `<div class="text-sm text-gray-900">${item[column.field] || '-'}</div>`;
                }
                
                row += '</td>';
            });

            if (this.config.actions) {
                row += '<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">';
                row += '<div class="flex items-center gap-2">';
                
                this.config.actions.forEach(action => {
                    if (!action.condition || action.condition(item)) {
                        row += `<button onclick="${action.onclick}(${item.id})" 
                                class="text-${action.color}-600 hover:text-${action.color}-800 p-2 hover:bg-${action.color}-50 rounded transition duration-200"
                                title="${action.title}">
                                <i class="fas fa-${action.icon}"></i>
                            </button>`;
                    }
                });
                
                row += '</div></td>';
            }

            row += '</tr>';
            return row;
        }).join('');

        tbody.parentElement.parentElement.classList.remove('hidden');
    }

    renderList(data) {
        const list = document.getElementById('data-list');
        if (!list) return;

        list.innerHTML = data.map(item => {
            let listItem = '<li class="py-4 flex justify-between items-center">';
            listItem += '<div class="flex-1">';
            listItem += `<h3 class="text-lg font-medium text-gray-900">${item[this.config.title_field] || '-'}</h3>`;
            
            if (this.config.subtitle_field) {
                listItem += `<p class="text-sm text-gray-500">${item[this.config.subtitle_field] || '-'}</p>`;
            }

            if (this.config.tags_field && item[this.config.tags_field]) {
                listItem += '<div class="flex flex-wrap gap-1 mt-2">';
                item[this.config.tags_field].forEach(tag => {
                    listItem += `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">${tag.name}</span>`;
                });
                listItem += '</div>';
            }

            listItem += '</div>';

            if (this.config.actions) {
                listItem += '<div class="flex items-center gap-2">';
                this.config.actions.forEach(action => {
                    if (!action.condition || action.condition(item)) {
                        listItem += `<button onclick="${action.onclick}(${item.id})" 
                                class="bg-${action.color}-500 hover:bg-${action.color}-700 text-white font-bold py-2 px-4 rounded transition duration-200">
                                ${action.text}
                            </button>`;
                    }
                });
                listItem += '</div>';
            }

            listItem += '</li>';
            return listItem;
        }).join('');

        list.parentElement.classList.remove('hidden');
    }
}

// ===== FUNCIONES DE UTILIDAD =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        return new Date(dateString).toLocaleDateString('es-ES');
    } catch (e) {
        return dateString;
    }
}

function showAlert(type, title, text, confirmText = 'OK') {
    const colors = {
        success: 'green',
        error: 'red',
        warning: 'yellow',
        info: 'blue'
    };

    const color = colors[type] || 'blue';
    
    // Usar SweetAlert2 si está disponible
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: type,
            title: title,
            text: text,
            confirmButtonText: confirmText,
            confirmButtonColor: `#${color === 'green' ? '16a34a' : color === 'red' ? 'dc2626' : color === 'yellow' ? 'd97706' : '3b82f6'}`
        });
    } else {
        alert(`${title}: ${text}`);
    }
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips si están disponibles
    if (typeof tippy !== 'undefined') {
        tippy('[data-tippy-content]');
    }
});
