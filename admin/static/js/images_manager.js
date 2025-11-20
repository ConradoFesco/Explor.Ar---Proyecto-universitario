/**
 * Gestión de imágenes para sitios históricos
 * Maneja subida múltiple, eliminación, ordenamiento y marcado de portada
 */

let imagesManager = {
    siteId: null,
    images: [],
    pendingImages: [], // Imágenes pendientes de subir (cuando no hay site_id)
    MAX_IMAGES_PER_SITE: 10, // Límite máximo de imágenes por sitio
    currentValidFiles: [], // Archivos válidos seleccionados actualmente
    previewImages: [], // Imágenes en previsualización con sus metadatos
    previewCoverIndex: null, // Índice de la imagen portada en la previsualización
    
    init: function(siteId) {
        console.log('imagesManager.init llamado con siteId:', siteId);
        this.siteId = siteId;
        this.setupUploadForm();
        if (siteId) {
            this.enableImageForm();
            this.loadImages();
        } else {
            // Modo creación: permitir seleccionar imágenes pero almacenarlas temporalmente
            this.enableImageForm();
            this.loadPendingImages();
        }
    },
    
    setupUploadForm: function() {
        const form = document.getElementById('upload-image-form');
        if (!form) return;
        
        const fileInput = document.getElementById('imagen-file');
        const uploadBtn = document.getElementById('btn-upload-images');
        const clearBtn = document.getElementById('btn-clear-selection');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });
        }
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                this.uploadSelectedImages();
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearFileSelection();
            });
        }
    },
    
    handleFileSelection: function(files) {
        if (!files || files.length === 0) {
            this.clearFileSelection();
            return;
        }
        
        const previewContainer = document.getElementById('selected-images-preview');
        const selectedList = document.getElementById('selected-images-list');
        const clearBtn = document.getElementById('btn-clear-selection');
        
        if (!previewContainer || !selectedList) return;
        
        // Calcular cuántas imágenes ya hay (cargadas + pendientes)
        const currentCount = this.images.length + this.pendingImages.length;
        const availableSlots = this.MAX_IMAGES_PER_SITE - currentCount;
        
        if (availableSlots <= 0) {
            this.showMessage(`Ya ha alcanzado el límite máximo de ${this.MAX_IMAGES_PER_SITE} imágenes por sitio.`, 'error');
            this.clearFileSelection();
            return;
        }
        
        // Validar archivos y tomar solo las primeras N válidas que no excedan el límite
        const validFiles = [];
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const maxSize = 5 * 1024 * 1024; // 5 MB
        let invalidCount = 0;
        let skippedCount = 0;
        
        for (let i = 0; i < files.length && validFiles.length < availableSlots; i++) {
            const file = files[i];
            
            if (!allowedTypes.includes(file.type)) {
                invalidCount++;
                continue;
            }
            
            if (file.size > maxSize) {
                invalidCount++;
                continue;
            }
            
            validFiles.push(file);
        }
        
        // Contar cuántas se saltaron por exceder el límite
        if (files.length > validFiles.length + invalidCount) {
            skippedCount = files.length - validFiles.length - invalidCount;
        }
        
        // Mostrar mensajes informativos
        if (invalidCount > 0) {
            this.showMessage(`${invalidCount} archivo(s) fueron rechazados por formato o tamaño inválido.`, 'error');
        }
        
        if (skippedCount > 0) {
            this.showMessage(`Solo se pueden agregar ${availableSlots} imagen(es) más. Se omitieron ${skippedCount} imagen(es) para no exceder el límite de ${this.MAX_IMAGES_PER_SITE}.`, 'warning');
        }
        
        if (validFiles.length === 0) {
            this.clearFileSelection();
            return;
        }
        
        if (validFiles.length < files.length - invalidCount) {
            this.showMessage(`Se seleccionaron ${validFiles.length} de ${files.length} imagen(es) válidas (límite: ${this.MAX_IMAGES_PER_SITE} imágenes por sitio).`, 'info');
        }
        
        // Guardar las imágenes válidas para procesamiento posterior
        // Nota: No podemos modificar directamente el input file, pero guardamos las válidas
        this.currentValidFiles = validFiles;
        
        // Inicializar array de previsualización con metadatos
        this.previewImages = validFiles.map((file, index) => ({
            file: file,
            index: index,
            titulo_alt: '',
            descripcion: '',
            isCover: false,
            order: index
        }));
        
        // Verificar si ya existe una portada en las imágenes cargadas
        const hasExistingCover = this.images.some(img => img.es_portada === true);
        
        // Solo marcar automáticamente la primera imagen como portada si:
        // - No hay imágenes cargadas
        // - No hay imágenes pendientes
        // - No hay una portada existente
        if (this.images.length === 0 && this.pendingImages.length === 0 && validFiles.length > 0 && !hasExistingCover) {
            this.previewCoverIndex = 0;
            this.previewImages[0].isCover = true;
        } else if (this.previewCoverIndex === null && validFiles.length > 0) {
            // Si ya hay imágenes o hay una portada existente, no marcar ninguna automáticamente
            this.previewCoverIndex = null;
        }
        
        // Mostrar previsualización de imágenes seleccionadas
        this.renderPreviewImages();
        
        previewContainer.style.display = 'block';
        if (clearBtn) clearBtn.style.display = 'inline-block';
    },
    
    renderPreviewImages: function() {
        const selectedList = document.getElementById('selected-images-list');
        if (!selectedList) return;
        
        // Ordenar por order
        const sorted = [...this.previewImages].sort((a, b) => a.order - b.order);
        
        selectedList.innerHTML = '';
        sorted.forEach((imgData, displayIndex) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const imageItem = this.createImagePreviewItem(imgData, displayIndex, e.target.result);
                selectedList.appendChild(imageItem);
            };
            reader.readAsDataURL(imgData.file);
        });
        
        // Configurar drag and drop para reordenar
        this.setupPreviewDragAndDrop();
    },
    
    createImagePreviewItem: function(imgData, displayIndex, previewUrl) {
        const div = document.createElement('div');
        div.className = `preview-image-item border-2 rounded-md p-3 bg-white ${imgData.isCover ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`;
        div.draggable = true;
        div.dataset.originalIndex = imgData.index;
        div.dataset.displayIndex = displayIndex;
        
        const coverBadge = imgData.isCover ? '<span class="inline-block bg-blue-500 text-white text-xs px-2 py-1 rounded mb-2">PORTADA</span>' : '';
        const coverButton = !imgData.isCover ? `<button type="button" onclick="imagesManager.setPreviewCover(${imgData.index})" class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded">Marcar como Portada</button>` : '';
        
        div.innerHTML = `
            <div class="flex gap-3">
                <div class="relative">
                    <span class="drag-handle-preview absolute top-1 left-1 bg-gray-800 bg-opacity-50 text-white px-2 py-1 rounded cursor-move text-xs" title="Arrastrar para reordenar">☰</span>
                    <img src="${previewUrl}" alt="Preview" class="w-24 h-24 object-cover rounded-md">
                </div>
                <div class="flex-1 space-y-2">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-700">${imgData.file.name}</p>
                            <p class="text-xs text-gray-500">${(imgData.file.size / 1024).toFixed(2)} KB</p>
                        </div>
                        <div class="flex flex-col items-end gap-1">
                            ${coverBadge}
                            ${coverButton}
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Título/Alt Text *</label>
                        <input type="text" class="image-title-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                               data-index="${imgData.index}" value="${imgData.titulo_alt || ''}" 
                               placeholder="Descripción breve" maxlength="255" required
                               onchange="imagesManager.updatePreviewMetadata(${imgData.index}, 'titulo_alt', this.value)">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Descripción (opcional)</label>
                        <textarea class="image-desc-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                                  data-index="${imgData.index}" rows="2" placeholder="Descripción adicional"
                                  onchange="imagesManager.updatePreviewMetadata(${imgData.index}, 'descripcion', this.value)">${imgData.descripcion || ''}</textarea>
                    </div>
                </div>
            </div>
        `;
        return div;
    },
    
    updatePreviewMetadata: function(index, field, value) {
        const imgData = this.previewImages.find(img => img.index === index);
        if (imgData) {
            imgData[field] = value;
        }
    },
    
    setPreviewCover: function(index) {
        // Desmarcar todas las portadas (sin confirmación)
        this.previewImages.forEach(img => {
            img.isCover = false;
        });
        
        // Marcar la seleccionada
        const imgData = this.previewImages.find(img => img.index === index);
        if (imgData) {
            imgData.isCover = true;
            this.previewCoverIndex = index;
        }
        
        // Re-renderizar
        this.renderPreviewImages();
    },
    
    setupPreviewDragAndDrop: function() {
        const container = document.getElementById('selected-images-list');
        if (!container) return;
        
        const items = container.querySelectorAll('.preview-image-item');
        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', item.dataset.originalIndex);
                item.style.opacity = '0.5';
                item.classList.add('dragging');
            });
            
            item.addEventListener('dragend', (e) => {
                item.style.opacity = '1';
                item.classList.remove('dragging');
            });
            
            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                const afterElement = this.getDragAfterElement(container, e.clientY);
                const dragging = container.querySelector('.dragging');
                if (dragging) {
                    if (afterElement == null) {
                        container.appendChild(dragging);
                    } else {
                        container.insertBefore(dragging, afterElement);
                    }
                }
            });
            
            item.addEventListener('drop', (e) => {
                e.preventDefault();
                const draggedIndex = parseInt(e.dataTransfer.getData('text/plain'));
                const targetIndex = parseInt(item.dataset.originalIndex);
                
                if (draggedIndex !== targetIndex) {
                    this.reorderPreviewImages(draggedIndex, targetIndex);
                }
            });
        });
    },
    
    reorderPreviewImages: function(fromIndex, toIndex) {
        const fromImg = this.previewImages.find(img => img.index === fromIndex);
        const toImg = this.previewImages.find(img => img.index === toIndex);
        
        if (fromImg && toImg) {
            // Intercambiar órdenes
            const tempOrder = fromImg.order;
            fromImg.order = toImg.order;
            toImg.order = tempOrder;
            
            // Re-renderizar
            this.renderPreviewImages();
        }
    },
    
    getDragAfterElement: function(container, y) {
        // Funciona tanto para preview como para imágenes cargadas
        const selector = container.id === 'selected-images-list' 
            ? '.preview-image-item:not(.dragging)' 
            : '.image-item:not(.dragging)';
        const draggableElements = [...container.querySelectorAll(selector)];
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
    
    clearFileSelection: function() {
        const fileInput = document.getElementById('imagen-file');
        const previewContainer = document.getElementById('selected-images-preview');
        const clearBtn = document.getElementById('btn-clear-selection');
        
        if (fileInput) fileInput.value = '';
        if (previewContainer) previewContainer.style.display = 'none';
        if (clearBtn) clearBtn.style.display = 'none';
        this.currentValidFiles = [];
        this.previewImages = [];
        this.previewCoverIndex = null;
    },
    
    uploadSelectedImages: async function() {
        // Usar las imágenes válidas que se procesaron en handleFileSelection
        const files = this.currentValidFiles;
        
        if (!files || files.length === 0) {
            this.showMessage('Por favor seleccione al menos una imagen válida', 'error');
            return;
        }
        
        // Verificar límite antes de procesar
        const currentCount = this.images.length + this.pendingImages.length;
        const availableSlots = this.MAX_IMAGES_PER_SITE - currentCount;
        
        if (availableSlots <= 0) {
            this.showMessage(`Ya ha alcanzado el límite máximo de ${this.MAX_IMAGES_PER_SITE} imágenes por sitio.`, 'error');
            return;
        }
        
        // Usar los datos de previsualización (que incluyen títulos, descripciones y orden)
        const sortedPreview = [...this.previewImages].sort((a, b) => a.order - b.order);
        const maxToProcess = Math.min(sortedPreview.length, availableSlots);
        
        // Validar que todos tengan título
        const imagesData = [];
        let coverSet = false;
        
        // Verificar si ya existe una portada en las imágenes cargadas
        const hasExistingCover = this.images.some(img => img.es_portada === true);
        
        for (let i = 0; i < maxToProcess; i++) {
            const imgData = sortedPreview[i];
            const tituloAlt = imgData.titulo_alt.trim();
            const descripcion = imgData.descripcion ? imgData.descripcion.trim() : null;
            
            if (!tituloAlt) {
                this.showMessage(`El título/alt es obligatorio para la imagen ${i + 1}`, 'error');
                return;
            }
            
            // Solo marcar como portada si:
            // 1. Es la primera imagen Y no hay imágenes cargadas Y no hay portada ya establecida, O
            // 2. El usuario explícitamente marcó esta imagen como portada en la previsualización Y no hay portada existente
            let isCover = false;
            if (!hasExistingCover) {
                // Si no hay portada existente, usar la lógica original
                isCover = (i === 0 && this.images.length === 0 && !coverSet) || imgData.isCover;
            } else {
                // Si ya hay una portada existente, solo marcar como portada si el usuario lo hizo explícitamente
                // y no hay otra portada ya marcada en esta carga
                isCover = imgData.isCover && !coverSet;
            }
            
            if (isCover) {
                coverSet = true;
            }
            
            imagesData.push({
                file: imgData.file,
                titulo_alt: tituloAlt,
                descripcion: descripcion,
                is_cover: isCover,
                order: i
            });
        }
        
        if (sortedPreview.length > maxToProcess) {
            this.showMessage(`Solo se procesarán ${maxToProcess} imagen(es) para no exceder el límite de ${this.MAX_IMAGES_PER_SITE}.`, 'warning');
        }
        
        if (this.siteId) {
            // Si ya hay site_id, subir inmediatamente
            await this.uploadMultipleImages(imagesData);
        } else {
            // Si no hay site_id, almacenar temporalmente
            this.pendingImages = this.pendingImages.concat(imagesData);
            console.log('Imágenes agregadas a la cola:', this.pendingImages.length);
            this.savePendingImages();
            this.showMessage(`${imagesData.length} imagen(es) agregada(s) a la cola. Se subirán cuando cree el sitio.`, 'success');
            this.clearFileSelection();
            // Forzar actualización del display
            setTimeout(() => {
                this.updatePendingImagesDisplay();
            }, 100);
        }
    },
    
    savePendingImages: async function() {
        // Guardar metadatos en localStorage (los archivos se mantienen en memoria)
        const pendingData = this.pendingImages.map(img => ({
            name: img.file.name,
            size: img.file.size,
            type: img.file.type,
            titulo_alt: img.titulo_alt,
            descripcion: img.descripcion,
            is_cover: img.is_cover || false
        }));
        
        localStorage.setItem('pending_site_images_meta', JSON.stringify(pendingData));
        this.updatePendingImagesDisplay();
    },
    
    uploadMultipleImages: async function(imagesData) {
        if (!this.siteId) {
            this.showMessage('No hay sitio asociado', 'error');
            return;
        }
        
        const formData = new FormData();
        let coverImageId = null;
        
        imagesData.forEach((imgData, index) => {
            formData.append('imagenes', imgData.file);
            formData.append('titulo_alt[]', imgData.titulo_alt);
            if (imgData.descripcion) {
                formData.append('descripcion[]', imgData.descripcion);
            }
            // Enviar información sobre cuál es la portada
            if (imgData.is_cover) {
                formData.append('cover_index', index);
            }
        });
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Si hay una imagen marcada como portada, marcarla en el servidor (sin confirmación)
                const coverIndex = imagesData.findIndex(img => img.is_cover);
                if (coverIndex !== -1 && data.images && data.images[coverIndex]) {
                    const coverImageId = data.images[coverIndex].id;
                    await this.setCover(coverImageId, false); // false = sin confirmación
                }
                
                this.showMessage(data.message || `Se subieron ${imagesData.length} imagen(es) correctamente`, 'success');
                this.clearFileSelection();
                setTimeout(() => {
                    this.loadImages();
                }, 500);
            } else {
                this.showMessage(data.error || 'Error al subir imágenes', 'error');
            }
        } catch (error) {
            this.showMessage('Error al subir imágenes: ' + error.message, 'error');
        }
    },
    
    
    loadPendingImages: function() {
        // Cargar metadatos de imágenes pendientes desde localStorage
        const stored = localStorage.getItem('pending_site_images_meta');
        if (stored) {
            try {
                const pendingData = JSON.parse(stored);
                // Solo mostramos que hay imágenes pendientes (los archivos se mantienen en memoria)
                if (pendingData.length > 0) {
                    this.updatePendingImagesDisplay();
                }
            } catch (e) {
                console.error('Error al cargar imágenes pendientes:', e);
            }
        }
    },
    
    updatePendingImagesDisplay: function() {
        console.log('updatePendingImagesDisplay llamado, pendingImages:', this.pendingImages.length);
        
        // Crear o actualizar contenedor de imágenes pendientes
        let container = document.getElementById('pending-images-container');
        const imagesSection = document.getElementById('images-section');
        
        if (!imagesSection) {
            console.warn('No se encontró la sección de imágenes');
            return;
        }
        
        if (this.pendingImages.length === 0) {
            if (container) {
                container.style.display = 'none';
            }
            return;
        }
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'pending-images-container';
            
            // Insertar después del formulario de subida, antes de "Imágenes del Sitio"
            const uploadForm = document.getElementById('upload-image-form');
            const imagesListContainer = document.getElementById('images-list-container');
            
            if (uploadForm && uploadForm.parentElement) {
                // Insertar después del div que contiene el formulario
                uploadForm.parentElement.insertAdjacentElement('afterend', container);
                console.log('Contenedor insertado después del formulario');
            } else if (imagesListContainer) {
                // Si no encontramos el formulario, insertar antes de la lista de imágenes
                imagesListContainer.insertAdjacentElement('beforebegin', container);
                console.log('Contenedor insertado antes de la lista de imágenes');
            } else {
                // Último recurso: insertar al final de la sección
                imagesSection.appendChild(container);
                console.log('Contenedor insertado al final de la sección');
            }
        }
        
        container.style.display = 'block';
        container.className = 'mb-6 p-4 border border-yellow-300 rounded-md bg-yellow-50';
        container.innerHTML = `
            <div id="pending-images-grid" class="space-y-3"></div>
        `;
        
        // Renderizar cada imagen pendiente
        const grid = document.getElementById('pending-images-grid');
        if (grid) {
            grid.innerHTML = '';
            console.log('Renderizando', this.pendingImages.length, 'imágenes pendientes');
            this.pendingImages.forEach((imgData, index) => {
                if (!imgData.file) {
                    console.warn('Imagen sin archivo en índice', index);
                    return;
                }
                const reader = new FileReader();
                reader.onload = (e) => {
                    const imageItem = this.createPendingImageItem(imgData, index, e.target.result);
                    grid.appendChild(imageItem);
                };
                reader.onerror = () => {
                    console.error('Error al leer el archivo:', imgData.file.name);
                };
                reader.readAsDataURL(imgData.file);
            });
        } else {
            console.error('No se encontró el grid para imágenes pendientes');
        }
    },
    
    createPendingImageItem: function(imgData, index, previewUrl) {
        const div = document.createElement('div');
        div.className = `pending-image-item border-2 rounded-md p-3 bg-white ${imgData.is_cover ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`;
        div.dataset.pendingIndex = index;
        
        const coverBadge = imgData.is_cover ? '<span class="inline-block bg-blue-500 text-white text-xs px-2 py-1 rounded mb-2">PORTADA</span>' : '';
        const coverButton = !imgData.is_cover ? `<button type="button" onclick="imagesManager.setPendingCover(${index})" class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded">Marcar como Portada</button>` : '';
        
        div.innerHTML = `
            <div class="flex gap-3">
                <div class="relative">
                    <img src="${previewUrl}" alt="Preview" class="w-24 h-24 object-cover rounded-md">
                </div>
                <div class="flex-1 space-y-2">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-700">${imgData.file.name}</p>
                            <p class="text-xs text-gray-500">${(imgData.file.size / 1024).toFixed(2)} KB</p>
                        </div>
                        <div class="flex flex-col items-end gap-1">
                            ${coverBadge}
                            ${coverButton}
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Título/Alt Text *</label>
                        <input type="text" class="pending-title-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                               value="${imgData.titulo_alt || ''}" 
                               placeholder="Descripción breve" maxlength="255" required
                               onchange="imagesManager.updatePendingImage(${index}, 'titulo_alt', this.value)">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Descripción (opcional)</label>
                        <textarea class="pending-desc-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                                  rows="2" placeholder="Descripción adicional"
                                  onchange="imagesManager.updatePendingImage(${index}, 'descripcion', this.value)">${imgData.descripcion || ''}</textarea>
                    </div>
                    <div class="flex justify-end">
                        <button type="button" onclick="imagesManager.removePendingImage(${index})" 
                                class="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded">
                            Eliminar
                        </button>
                    </div>
                </div>
            </div>
        `;
        return div;
    },
    
    updatePendingImage: function(index, field, value) {
        if (this.pendingImages[index]) {
            if (field === 'descripcion') {
                this.pendingImages[index][field] = value.trim() || null;
            } else {
                this.pendingImages[index][field] = value.trim();
            }
            this.savePendingImages();
        }
    },
    
    setPendingCover: function(index) {
        // Desmarcar todas las portadas
        this.pendingImages.forEach(img => {
            img.is_cover = false;
        });
        
        // Marcar la seleccionada
        if (this.pendingImages[index]) {
            this.pendingImages[index].is_cover = true;
        }
        
        // Actualizar display
        this.updatePendingImagesDisplay();
        this.savePendingImages();
    },
    
    removePendingImage: function(index) {
        if (confirm('¿Está seguro de que desea eliminar esta imagen de la cola?')) {
            this.pendingImages.splice(index, 1);
            this.updatePendingImagesDisplay();
            this.savePendingImages();
            this.showMessage('Imagen eliminada de la cola', 'success');
        }
    },
    
    uploadPendingImages: async function(siteId) {
        if (this.pendingImages.length === 0) return;
        
        this.siteId = siteId;
        await this.uploadMultipleImages(this.pendingImages);
        this.pendingImages = [];
        localStorage.removeItem('pending_site_images_meta');
        this.updatePendingImagesDisplay();
    },
    
    loadImages: async function() {
        if (!this.siteId) {
            console.error('imagesManager: siteId no está definido');
            return;
        }
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error al cargar imágenes:', response.status, errorText);
                this.showMessage(`Error al cargar imágenes (${response.status})`, 'error');
                return;
            }
            
            const data = await response.json();
            console.log('Imágenes cargadas:', data);
            
            if (data.success) {
                this.images = data.images || [];
                console.log('Total de imágenes:', this.images.length);
                this.renderImages();
            } else {
                this.showMessage(data.error || 'Error al cargar imágenes', 'error');
            }
        } catch (error) {
            console.error('Error al cargar imágenes:', error);
            this.showMessage('Error al cargar imágenes: ' + error.message, 'error');
        }
    },
    
    renderImages: function() {
        const container = document.getElementById('images-grid');
        if (!container) {
            console.error('imagesManager: No se encontró el contenedor images-grid');
            return;
        }
        
        const noImagesMsg = document.getElementById('no-images-message');
        
        if (this.images.length === 0) {
            if (noImagesMsg) {
                noImagesMsg.style.display = 'block';
            }
            container.innerHTML = '<p class="text-gray-500 col-span-full">No hay imágenes cargadas aún.</p>';
            console.log('No hay imágenes para mostrar');
            return;
        }
        
        if (noImagesMsg) {
            noImagesMsg.style.display = 'none';
        }
        
        console.log('Renderizando', this.images.length, 'imágenes');
        
        // Ordenar por orden
        const sortedImages = [...this.images].sort((a, b) => a.orden - b.orden);
        
        const html = sortedImages.map((img, index) => {
            const isCover = img.es_portada;
            console.log(`Renderizando imagen ${index + 1}:`, img.id, img.titulo_alt, img.url_publica);
            return `
                <div class="image-item ${isCover ? 'cover' : ''}" data-image-id="${img.id}">
                    ${isCover ? '<span class="cover-badge">PORTADA</span>' : ''}
                    <img src="${img.url_publica}" alt="${img.titulo_alt}" loading="lazy" onerror="console.error('Error al cargar imagen:', this.src)">
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
        
        container.innerHTML = html;
        console.log('HTML generado y insertado en el contenedor');
        
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
    
    setCover: async function(imageId, showConfirm = true) {
        // Solo mostrar confirmación si se solicita explícitamente (para acciones manuales del usuario)
        if (showConfirm && !confirm('¿Desea marcar esta imagen como portada?')) {
            return;
        }
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes/${imageId}/portada`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (showConfirm) {
                    this.showMessage('Imagen marcada como portada', 'success');
                }
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
    
    disableImageForm: function() {
        // Ya no deshabilitamos, siempre permitimos seleccionar
    },
    
    enableImageForm: function() {
        // Siempre habilitado
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
        
        let bgColor = 'bg-blue-500';
        if (type === 'success') {
            bgColor = 'bg-green-500';
        } else if (type === 'error') {
            bgColor = 'bg-red-500';
        } else if (type === 'warning') {
            bgColor = 'bg-yellow-500';
        } else if (type === 'info') {
            bgColor = 'bg-blue-500';
        }
        
        const messageEl = document.createElement('div');
        messageEl.className = `${bgColor} text-white px-4 py-2 rounded shadow-lg mb-2`;
        messageEl.textContent = message;
        messageContainer.appendChild(messageEl);
        
        // Mensajes de advertencia e info duran más tiempo
        const duration = (type === 'warning' || type === 'info') ? 5000 : 3000;
        
        setTimeout(() => {
            messageEl.remove();
        }, duration);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const siteIdInput = document.getElementById('site-id-for-images');
    const siteId = siteIdInput && siteIdInput.value ? parseInt(siteIdInput.value) : null;
    imagesManager.init(siteId);
});
