/**
 * Gestión de imágenes para sitios históricos
 * Maneja subida, eliminación, ordenamiento y marcado de portada
 */

let imagesManager = {
    siteId: null,
    images: [],
    
    init: function(siteId) {
        this.siteId = siteId;
        this.setupUploadForm();
        this.loadImages();
    },
    
    setupUploadForm: function() {
        const form = document.getElementById('upload-image-form');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadImage();
        });
    },
    
    uploadImage: async function() {
        const form = document.getElementById('upload-image-form');
        const formData = new FormData(form);
        const fileInput = document.getElementById('imagen-file');
        const tituloAlt = document.getElementById('titulo-alt').value.trim();
        
        if (!fileInput.files[0]) {
            this.showMessage('Por favor seleccione un archivo', 'error');
            return;
        }
        
        if (!tituloAlt) {
            this.showMessage('El título/alt es obligatorio', 'error');
            return;
        }
        
        // Validar tamaño (5 MB)
        const file = fileInput.files[0];
        if (file.size > 5 * 1024 * 1024) {
            this.showMessage('El archivo excede el tamaño máximo de 5 MB', 'error');
            return;
        }
        
        // Validar formato
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            this.showMessage('Formato no permitido. Use JPG, PNG o WEBP', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('Imagen subida correctamente', 'success');
                form.reset();
                this.loadImages();
            } else {
                this.showMessage(data.error || 'Error al subir imagen', 'error');
            }
        } catch (error) {
            this.showMessage('Error al subir imagen: ' + error.message, 'error');
        }
    },
    
    loadImages: async function() {
        if (!this.siteId) return;
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`);
            const data = await response.json();
            
            if (data.success) {
                this.images = data.images || [];
                this.renderImages();
            } else {
                this.showMessage('Error al cargar imágenes', 'error');
            }
        } catch (error) {
            this.showMessage('Error al cargar imágenes: ' + error.message, 'error');
        }
    },
    
    renderImages: function() {
        const container = document.getElementById('images-grid');
        if (!container) return;
        
        const noImagesMsg = document.getElementById('no-images-message');
        
        if (this.images.length === 0) {
            if (noImagesMsg) noImagesMsg.style.display = 'block';
            container.innerHTML = '<p class="text-gray-500 col-span-full">No hay imágenes cargadas aún.</p>';
            return;
        }
        
        if (noImagesMsg) noImagesMsg.style.display = 'none';
        
        // Ordenar por orden
        const sortedImages = [...this.images].sort((a, b) => a.orden - b.orden);
        
        container.innerHTML = sortedImages.map((img, index) => {
            const isCover = img.es_portada;
            return `
                <div class="image-item ${isCover ? 'cover' : ''}" data-image-id="${img.id}">
                    ${isCover ? '<span class="cover-badge">PORTADA</span>' : ''}
                    <img src="${img.url_publica}" alt="${img.titulo_alt}" loading="lazy">
                    <div class="image-info">
                        <p class="text-sm font-medium text-gray-800 truncate" title="${img.titulo_alt}">${img.titulo_alt}</p>
                        ${img.descripcion ? `<p class="text-xs text-gray-600 mt-1 truncate" title="${img.descripcion}">${img.descripcion}</p>` : ''}
                    </div>
                    <div class="image-actions">
                        <span class="drag-handle" title="Arrastrar para reordenar">☰</span>
                        <div class="flex gap-2">
                            ${!isCover ? `<button onclick="imagesManager.setCover(${img.id})" class="text-xs bg-blue-500 hover:bg-blue-600 px-2 py-1 rounded" title="Marcar como portada">Portada</button>` : ''}
                            <button onclick="imagesManager.deleteImage(${img.id})" class="text-xs bg-red-500 hover:bg-red-600 px-2 py-1 rounded" title="Eliminar">Eliminar</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Configurar drag and drop para reordenar
        this.setupDragAndDrop();
    },
    
    setupDragAndDrop: function() {
        const container = document.getElementById('images-grid');
        if (!container) return;
        
        // Implementación simple de drag and drop
        const items = container.querySelectorAll('.image-item');
        items.forEach(item => {
            item.draggable = true;
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', item.dataset.imageId);
                item.style.opacity = '0.5';
            });
            item.addEventListener('dragend', (e) => {
                item.style.opacity = '1';
            });
            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                const afterElement = this.getDragAfterElement(container, e.clientY);
                const dragging = document.querySelector('.dragging');
                if (afterElement == null) {
                    container.appendChild(item);
                } else {
                    container.insertBefore(item, afterElement);
                }
            });
        });
    },
    
    getDragAfterElement: function(container, y) {
        const draggableElements = [...container.querySelectorAll('.image-item:not(.dragging)')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    },
    
    setCover: async function(imageId) {
        if (!confirm('¿Desea marcar esta imagen como portada?')) return;
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes/${imageId}/portada`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('Imagen marcada como portada', 'success');
                this.loadImages();
            } else {
                this.showMessage(data.error || 'Error al marcar portada', 'error');
            }
        } catch (error) {
            this.showMessage('Error al marcar portada: ' + error.message, 'error');
        }
    },
    
    deleteImage: async function(imageId) {
        const image = this.images.find(img => img.id === imageId);
        if (!image) return;
        
        if (image.es_portada) {
            this.showMessage('No se puede eliminar la imagen portada. Primero debe cambiar la portada a otra imagen.', 'error');
            return;
        }
        
        if (!confirm('¿Está seguro de que desea eliminar esta imagen?')) return;
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes/${imageId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('Imagen eliminada correctamente', 'success');
                this.loadImages();
            } else {
                this.showMessage(data.error || 'Error al eliminar imagen', 'error');
            }
        } catch (error) {
            this.showMessage('Error al eliminar imagen: ' + error.message, 'error');
        }
    },
    
    showMessage: function(message, type) {
        // Buscar contenedor de mensajes o crear uno
        let messageContainer = document.getElementById('image-message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'image-message-container';
            messageContainer.className = 'fixed top-4 right-4 z-50';
            document.body.appendChild(messageContainer);
        }
        
        const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
        const messageEl = document.createElement('div');
        messageEl.className = `${bgColor} text-white px-4 py-2 rounded shadow-lg mb-2`;
        messageEl.textContent = message;
        messageContainer.appendChild(messageEl);
        
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const siteIdInput = document.getElementById('site-id-for-images');
    if (siteIdInput && siteIdInput.value) {
        imagesManager.init(parseInt(siteIdInput.value));
    }
});


