// Configuración global para tags
let currentPage = 1;
let totalPages = 1;
let currentSortBy = 'name';
let currentSortOrder = 'asc';
let currentSearch = '';
let editingTagId = null;

// Cargar tags al inicializar
document.addEventListener('DOMContentLoaded', function() {
    loadTags();
    setupEventListeners();
});

function setupEventListeners() {
    // Event listeners para búsqueda y ordenamiento
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    const sortBySelect = document.getElementById('sortBy');
    if (sortBySelect) {
        sortBySelect.addEventListener('change', handleSortChange);
    }

    const sortOrderSelect = document.getElementById('sortOrder');
    if (sortOrderSelect) {
        sortOrderSelect.addEventListener('change', handleSortChange);
    }
    
    // Event listener para el formulario de tag
    const tagForm = document.getElementById('tagForm');
    if (tagForm) {
        tagForm.addEventListener('submit', handleTagSubmit);
    }
    
    // Event listener para generar slug automáticamente
    const tagNameInput = document.getElementById('tagName');
    if (tagNameInput) {
        tagNameInput.addEventListener('input', generateSlug);
    }
}

// Función para cargar tags
async function loadTags() {
    try {
        showLoading(true);
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 25,
            sort_by: currentSortBy,
            sort_order: currentSortOrder
        });
        
        if (currentSearch) {
            params.append('search', currentSearch);
        }
        
        console.log('Cargando tags desde:', `/api/tags?${params}`);
        const response = await fetch(`/api/tags?${params}`);
        console.log('Respuesta de la API:', response.status, response.statusText);
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (response.ok) {
            displayTags(data.tags);
            updatePagination(data.pagination);
        } else {
            throw new Error(data.error || 'Error al cargar tags');
        }
    } catch (error) {
        console.error('Error:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los tags: ' + error.message,
                confirmButtonColor: '#dc2626'
            });
        } else {
            alert('Error al cargar los tags: ' + error.message);
        }
    } finally {
        showLoading(false);
    }
}

// Función para mostrar/ocultar loading
function showLoading(show) {
    const loadingMessage = document.getElementById('loading-message');
    const tagsContainer = document.getElementById('tags-container');
    const noTagsMessage = document.getElementById('no-tags-message');
    
    if (show) {
        if (loadingMessage) loadingMessage.classList.remove('hidden');
        if (tagsContainer) tagsContainer.classList.add('hidden');
        if (noTagsMessage) noTagsMessage.classList.add('hidden');
    } else {
        if (loadingMessage) loadingMessage.classList.add('hidden');
    }
}

// Función para mostrar tags en la tabla
function displayTags(tags) {
    const tbody = document.getElementById('tags-table-body');
    const tagsContainer = document.getElementById('tags-container');
    const noTagsMessage = document.getElementById('no-tags-message');
    
    console.log('displayTags llamada con:', tags.length, 'tags');
    console.log('Elementos encontrados:', {
        tbody: !!tbody,
        tagsContainer: !!tagsContainer,
        noTagsMessage: !!noTagsMessage
    });
    
    if (!tbody || !tagsContainer || !noTagsMessage) {
        console.error('Elementos del DOM no encontrados');
        return;
    }
    
    if (tags.length === 0) {
        console.log('No hay tags para mostrar');
        tagsContainer.classList.add('hidden');
        noTagsMessage.classList.remove('hidden');
        return;
    }
    
    console.log('Renderizando', tags.length, 'tags en la tabla');
    tbody.innerHTML = tags.map(tag => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${tag.name}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">${tag.slug}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">${new Date(tag.created_at).toLocaleDateString()}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">${tag.sites_count || 0} sitios</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                    <button onclick="editTag(${tag.id}, '${tag.name}', '${tag.slug}')" 
                        class="text-blue-600 hover:text-blue-800 p-2 hover:bg-blue-50 rounded transition duration-200"
                        title="Editar tag">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                    </button>
                    <button onclick="showDeleteModal(${tag.id}, '${tag.name}', ${tag.sites_count || 0})" 
                        class="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded transition duration-200"
                        title="Eliminar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    tagsContainer.classList.remove('hidden');
    noTagsMessage.classList.add('hidden');
    console.log('Tags renderizados correctamente');
}

// Función para actualizar paginación
function updatePagination(pagination) {
    const controls = document.getElementById('pagination-controls');
    const info = document.getElementById('pagination-info');
    
    if (!controls || !info) return;
    
    if (pagination.total_pages <= 1) {
        controls.classList.add('hidden');
        info.classList.add('hidden');
        return;
    }
    
    currentPage = pagination.current_page;
    totalPages = pagination.total_pages;
    
    let html = '';
    
    // Botón anterior
    if (pagination.has_prev) {
        html += `<button onclick="changePage(${pagination.prev_page})" 
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200">Anterior</button>`;
    }
    
    // Números de página
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage;
        html += `<button onclick="changePage(${i})" 
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg ${isActive ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'}">${i}</button>`;
    }
    
    // Botón siguiente
    if (pagination.has_next) {
        html += `<button onclick="changePage(${pagination.next_page})" 
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200">Siguiente</button>`;
    }
    
    controls.innerHTML = html;
    controls.classList.remove('hidden');
    
    // Información de paginación
    info.textContent = `Mostrando ${pagination.start} a ${pagination.end} de ${pagination.total} tags`;
    info.classList.remove('hidden');
}

// Función para cambiar página
function changePage(page) {
    currentPage = page;
    loadTags();
}

// Función para manejar búsqueda
function handleSearch(event) {
    currentSearch = event.target.value;
    currentPage = 1;
    loadTags();
}

// Función para manejar cambio de ordenamiento
function handleSortChange() {
    const sortBySelect = document.getElementById('sortBy');
    const sortOrderSelect = document.getElementById('sortOrder');
    
    if (sortBySelect) currentSortBy = sortBySelect.value;
    if (sortOrderSelect) currentSortOrder = sortOrderSelect.value;
    
    currentPage = 1;
    loadTags();
}

// Función debounce para búsqueda
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

// Funciones del modal de tag
function showCreateTagModal() {
    editingTagId = null;
    const modalTitle = document.getElementById('tag-modal-title');
    const submitBtn = document.getElementById('tagSubmitBtn');
    const tagForm = document.getElementById('tagForm');
    const tagModal = document.getElementById('tag-modal');
    
    if (modalTitle) modalTitle.textContent = 'Agregar Tag';
    if (submitBtn) submitBtn.textContent = 'Guardar';
    if (tagForm) tagForm.reset();
    if (tagModal) tagModal.classList.remove('hidden');
    
    clearErrors();
    // Generar slug vacío inicialmente
    const tagSlug = document.getElementById('tagSlug');
    if (tagSlug) tagSlug.value = '';
}

function editTag(id, name, slug) {
    editingTagId = id;
    const modalTitle = document.getElementById('tag-modal-title');
    const submitBtn = document.getElementById('tagSubmitBtn');
    const tagName = document.getElementById('tagName');
    const tagModal = document.getElementById('tag-modal');
    
    if (modalTitle) modalTitle.textContent = 'Editar Tag';
    if (submitBtn) submitBtn.textContent = 'Actualizar';
    if (tagName) tagName.value = name;
    if (tagModal) tagModal.classList.remove('hidden');
    
    // Generar slug automáticamente desde el nombre al editar
    generateSlug();
    clearErrors();
}

function closeTagModal() {
    const tagModal = document.getElementById('tag-modal');
    if (tagModal) {
        tagModal.classList.add('hidden');
    }
    editingTagId = null;
}

function clearErrors() {
    const tagNameError = document.getElementById('tagNameError');
    if (tagNameError) {
        tagNameError.classList.add('hidden');
    }
}

function generateSlug() {
    const nameInput = document.getElementById('tagName');
    const slugInput = document.getElementById('tagSlug');
    
    if (!nameInput || !slugInput) return;
    
    const name = nameInput.value;
    
    // Siempre generar el slug automáticamente desde el nombre
    slugInput.value = name.toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
}

// Función para manejar envío del formulario
async function handleTagSubmit(event) {
    event.preventDefault();
    
    const nameInput = document.getElementById('tagName');
    if (!nameInput) return;
    
    const name = nameInput.value.trim();
    
    if (!name) {
        const tagNameError = document.getElementById('tagNameError');
        if (tagNameError) {
            tagNameError.classList.remove('hidden');
        }
        return;
    }
    
    try {
        const url = editingTagId ? `/api/tags/${editingTagId}` : '/api/tags';
        const method = editingTagId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const wasEditing = !!editingTagId; // Guardar el estado antes de cerrar el modal
            closeTagModal();
            loadTags();
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: wasEditing ? 'Tag actualizado' : 'Tag creado',
                    text: `"${data.name}" ha sido ${wasEditing ? 'actualizado' : 'creado'} correctamente`,
                    confirmButtonColor: '#16a34a',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                alert(`Tag ${wasEditing ? 'actualizado' : 'creado'} correctamente`);
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al guardar el tag');
        }
    } catch (error) {
        console.error('Error:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message,
                confirmButtonColor: '#dc2626'
            });
        } else {
            alert('Error: ' + error.message);
        }
    }
}

// Funciones del modal de eliminación
let tagToDelete = null;

function showDeleteModal(id, name, sitesCount) {
    tagToDelete = id;
    const message = sitesCount > 0 
        ? `No se puede eliminar el tag "${name}" porque está asociado a ${sitesCount} sitio(s) histórico(s).`
        : `¿Estás seguro de que deseas eliminar el tag "${name}"?`;
    
    const deleteMessage = document.getElementById('deleteMessage');
    const buttonsContainer = document.getElementById('deleteModalButtons');
    const deleteModal = document.getElementById('delete-modal');
    
    if (deleteMessage) deleteMessage.textContent = message;
    
    if (buttonsContainer) {
        if (sitesCount > 0) {
            // Si el tag tiene sitios asociados, solo mostrar botón "Entendido"
            buttonsContainer.innerHTML = `
                <button onclick="closeDeleteModal()" 
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200">
                    Entendido
                </button>
            `;
        } else {
            // Si no tiene sitios asociados, mostrar botones de Cancelar y Eliminar
            buttonsContainer.innerHTML = `
                <button onclick="closeDeleteModal()" 
                    class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200">
                    Cancelar
                </button>
                <button onclick="deleteTag()" id="confirmDeleteBtn" 
                    class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition duration-200">
                    Eliminar
                </button>
            `;
        }
    }
    
    if (deleteModal) {
        deleteModal.classList.remove('hidden');
    }
}

function closeDeleteModal() {
    const deleteModal = document.getElementById('delete-modal');
    if (deleteModal) {
        deleteModal.classList.add('hidden');
    }
    tagToDelete = null;
}

async function deleteTag() {
    if (!tagToDelete) return;
    
    try {
        const response = await fetch(`/api/tags/${tagToDelete}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            closeDeleteModal();
            loadTags();
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: 'Tag eliminado',
                    text: 'El tag ha sido eliminado correctamente',
                    confirmButtonColor: '#16a34a',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                alert('Tag eliminado correctamente');
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al eliminar el tag');
        }
    } catch (error) {
        console.error('Error:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message,
                confirmButtonColor: '#dc2626'
            });
        } else {
            alert('Error: ' + error.message);
        }
    }
}