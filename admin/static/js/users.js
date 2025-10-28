// Configuración global para usuarios
let currentPage = 1;
const perPage = 25;
let currentFilters = {
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc',
    activo: '',
    rol: ''
};

// Cargar usuarios al inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadUsers(currentPage);
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
                loadUsers(currentPage);
            }, 500); // Debounce de 500ms
        });
    }

    // Ordenamiento
    const sortBySelect = document.getElementById('sort-by');
    if (sortBySelect) {
        sortBySelect.addEventListener('change', (e) => {
            currentFilters.sort_by = e.target.value;
            currentPage = 1;
            loadUsers(currentPage);
        });
    }

    const sortOrderSelect = document.getElementById('sort-order');
    if (sortOrderSelect) {
        sortOrderSelect.addEventListener('change', (e) => {
            currentFilters.sort_order = e.target.value;
            currentPage = 1;
            loadUsers(currentPage);
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
    const filterActive = document.getElementById('filter-active');
    if (filterActive) {
        filterActive.addEventListener('change', (e) => {
            currentFilters.activo = e.target.value;
        });
    }

    const filterRole = document.getElementById('filter-role');
    if (filterRole) {
        filterRole.addEventListener('change', (e) => {
            currentFilters.rol = e.target.value;
        });
    }

    // Botones de filtros
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            currentPage = 1;
            loadUsers(currentPage);
        });
    }

    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            clearFilters();
        });
    }

    // Modal de eliminación
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', performDeleteUser);
    }

    const cancelDeleteBtn = document.getElementById('cancelDelete');
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }
}

function clearFilters() {
    currentFilters = {
        search: '',
        sort_by: 'created_at',
        sort_order: 'desc',
        activo: '',
        rol: ''
    };

    // Limpiar inputs
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';

    const sortBySelect = document.getElementById('sort-by');
    if (sortBySelect) sortBySelect.value = 'created_at';

    const sortOrderSelect = document.getElementById('sort-order');
    if (sortOrderSelect) sortOrderSelect.value = 'desc';

    const filterActive = document.getElementById('filter-active');
    if (filterActive) filterActive.value = '';

    const filterRole = document.getElementById('filter-role');
    if (filterRole) filterRole.value = '';

    currentPage = 1;
    loadUsers(currentPage);
}

function buildApiUrl(page) {
    const params = new URLSearchParams({
        page: page,
        per_page: perPage,
        sort_by: currentFilters.sort_by,
        sort_order: currentFilters.sort_order
    });

    if (currentFilters.search) params.append('email', currentFilters.search);
    if (currentFilters.activo) params.append('activo', currentFilters.activo);
    if (currentFilters.rol) params.append('rol', currentFilters.rol);

    return `/api/users?${params.toString()}`;
}

function getInitials(name, lastName) {
    const firstInitial = name ? name.charAt(0).toUpperCase() : '';
    const lastInitial = lastName ? lastName.charAt(0).toUpperCase() : '';
    return firstInitial || lastInitial || '?';
}

function getAvatarColor(index) {
    const colors = [
        'bg-blue-200 text-blue-700',
        'bg-green-200 text-green-700',
        'bg-purple-200 text-purple-700',
        'bg-pink-200 text-pink-700',
        'bg-yellow-200 text-yellow-700',
        'bg-indigo-200 text-indigo-700'
    ];
    return colors[index % colors.length];
}

function loadUsers(page) {
    const usersContainer = document.getElementById('users-container');
    const usersTableBody = document.getElementById('users-table-body');
    const loadingMessage = document.getElementById('loading-message');
    const noUsersMessage = document.getElementById('no-users-message');
    const paginationControls = document.getElementById('pagination-controls');
    const paginationInfo = document.getElementById('pagination-info');

    console.log('loadUsers llamada para página:', page);
    console.log('Elementos encontrados:', {
        usersContainer: !!usersContainer,
        usersTableBody: !!usersTableBody,
        loadingMessage: !!loadingMessage,
        noUsersMessage: !!noUsersMessage
    });

    // Limpiar contenido anterior
    if (usersTableBody) usersTableBody.innerHTML = '';
    if (paginationControls) paginationControls.innerHTML = '';
    if (paginationInfo) paginationInfo.innerHTML = '';

    // Mostrar loading
    if (loadingMessage) loadingMessage.classList.remove('hidden');
    if (usersContainer) usersContainer.classList.add('hidden');
    if (noUsersMessage) noUsersMessage.classList.add('hidden');
    if (paginationControls) paginationControls.classList.add('hidden');
    if (paginationInfo) paginationInfo.classList.add('hidden');

    // Agregar timestamp para evitar caché
    const timestamp = new Date().getTime();
    const API_URL = buildApiUrl(page) + `&_=${timestamp}`;

    console.log('Cargando usuarios desde:', API_URL);
    
    fetch(API_URL, {
        cache: 'no-store',
        headers: {
            'Cache-Control': 'no-cache'
        }
    })
        .then(response => {
            console.log('Respuesta de la API:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`Error en la red: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);
            if (loadingMessage) loadingMessage.classList.add('hidden');
            
            if (!data.users || data.users.length === 0) {
                console.log('No hay usuarios para mostrar');
                if (noUsersMessage) noUsersMessage.classList.remove('hidden');
                return;
            }

            // Mostrar usuarios en tabla
            if (usersTableBody && usersContainer) {
                console.log('Renderizando', data.users.length, 'usuarios en la tabla');
                usersContainer.classList.remove('hidden');
                
                usersTableBody.innerHTML = data.users.map((user, index) => {
                    const initials = getInitials(user.name, user.last_name);
                    const avatarColor = getAvatarColor(index);
                    const activeStatus = user.active !== false;
                    
                    // Generar texto de roles
                    const userRoles = user.roles || [];
                    const userRole = userRoles.length > 0 ? userRoles.join('/') : 'Sin roles';
                    
                    const createdDate = user.created_at ? new Date(user.created_at).toISOString().split('T')[0] : '2024-01-15';
                    
                    // Verificar si el usuario puede ser editado o eliminado
                    const isSuperAdmin = userRoles.some(role => role.toLowerCase() === 'superadmin');
                    const isCurrentUser = user.id === window.currentUserId;
                    const canEdit = !isSuperAdmin || isCurrentUser;
                    const canDelete = !isSuperAdmin && !isCurrentUser;
                    
                    // Generar botón de editar condicionalmente
                    const editButton = canEdit ? `
                        <button onclick="window.location.href='/users/${user.id}/editar'" 
                            class="text-blue-600 hover:text-blue-800 p-2 hover:bg-blue-50 rounded transition duration-200"
                            title="Editar usuario">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </button>
                    ` : `
                        <button disabled
                            class="text-gray-300 p-2 cursor-not-allowed rounded transition duration-200"
                            title="No puedes editar a otro SuperAdmin">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </button>
                    `;
                    
                    // Generar botón de eliminar condicionalmente
                    const deleteButton = canDelete ? `
                        <button onclick="openDeleteModal(${user.id}, '${user.name} ${user.last_name}')" 
                            class="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded transition duration-200"
                            title="Eliminar">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    ` : `
                        <button disabled
                            class="text-gray-300 p-2 cursor-not-allowed rounded transition duration-200"
                            title="${isSuperAdmin ? 'No se puede eliminar SuperAdmin' : 'No puedes eliminarte a ti mismo'}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                    `;
                    
                    return `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="w-10 h-10 rounded-full ${avatarColor} flex items-center justify-center font-semibold text-sm flex-shrink-0 mr-3">
                                        ${initials}
                                    </div>
                                    <div>
                                        <div class="text-sm font-medium text-gray-900">${user.name} ${user.last_name}</div>
                                        <div class="text-sm text-gray-500">${user.mail}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">${userRole}</div>
                                <div class="text-sm text-gray-500">${createdDate}</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${activeStatus ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                    ${activeStatus ? 'Activo' : 'Inactivo'}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <div class="flex items-center gap-2">
                                    ${editButton}
                                    ${deleteButton}
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
                
                console.log('Usuarios renderizados correctamente');
            }

            // Mostrar controles de paginación
            renderPagination(data.pagination);
            currentPage = page;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            if (loadingMessage) {
                loadingMessage.textContent = `Error al cargar los datos: ${error.message}`;
            }
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
    paginationInfo.innerHTML = `Mostrando ${startItem}-${endItem} de ${pagination.total} usuarios`;
    paginationInfo.classList.remove('hidden');
    
    // Botón Anterior
    const prevButton = document.createElement('button');
    prevButton.innerHTML = '← Anterior';
    prevButton.disabled = !pagination.has_prev;
    prevButton.onclick = () => loadUsers(pagination.prev_num);
    prevButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
    paginationControls.appendChild(prevButton);
    
    // Números de página
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    if (startPage > 1) {
        const firstButton = document.createElement('button');
        firstButton.textContent = '1';
        firstButton.onclick = () => loadUsers(1);
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
        pageButton.onclick = () => loadUsers(i);
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
        lastButton.onclick = () => loadUsers(pagination.pages);
        lastButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200';
        paginationControls.appendChild(lastButton);
    }
    
    // Botón Siguiente
    const nextButton = document.createElement('button');
    nextButton.innerHTML = 'Siguiente →';
    nextButton.disabled = !pagination.has_next;
    nextButton.onclick = () => loadUsers(pagination.next_num);
    nextButton.className = 'px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
    paginationControls.appendChild(nextButton);
    
    paginationControls.classList.remove('hidden');
}

// Funcionalidad del modal de eliminación
let userToDelete = null;

function openDeleteModal(userId, userName) {
    userToDelete = userId;
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = userName;
    }
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    const deleteReason = document.getElementById('deleteReason');
    if (deleteReason) {
        deleteReason.value = '';
    }
    userToDelete = null;
}

function performDeleteUser() {
    if (!userToDelete) return;

    const reasonElement = document.getElementById('deleteReason');
    const reason = reasonElement ? reasonElement.value : '';

    const deletePayload = {
        data_user: {
            id: window.currentUserId
        },
        reason: reason
    };

    fetch(`/api/users/${userToDelete}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(deletePayload)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => {
                throw new Error(error.error || 'Error al eliminar usuario');
            });
        }
    })
    .then(data => {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: '¡Eliminado!',
                text: data.message || 'Usuario eliminado correctamente',
                confirmButtonColor: '#3B82F6',
                timer: 2000,
                showConfirmButton: false
            });
        } else {
            alert('Usuario eliminado correctamente');
        }
        loadUsers(currentPage); // Recargar la lista actual
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error al eliminar usuario',
                confirmButtonColor: '#dc2626'
            });
        } else {
            alert('Error al eliminar usuario: ' + error.message);
        }
    })
    .finally(() => {
        closeDeleteModal();
    });
}

// Recargar cuando la página vuelve a ser visible (volviendo del formulario de edición)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        loadUsers(currentPage);
    }
});