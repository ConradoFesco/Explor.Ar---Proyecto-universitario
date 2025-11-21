let imagesManager = {
    siteId: null,
    images: [],
    pendingImages: [],
    MAX_IMAGES_PER_SITE: 10,
    currentValidFiles: [],
    previewImages: [],
    renderCounter: 0,
    
    init: function(siteId) {
        this.siteId = siteId;
        this.setupUploadForm();
        if (siteId) {
            this.loadImages();
        } else {
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
        
        const currentCount = this.images.length + this.pendingImages.length;
        const availableSlots = this.MAX_IMAGES_PER_SITE - currentCount;
        
        if (availableSlots <= 0) {
            this.showMessage(`Ya ha alcanzado el límite máximo de ${this.MAX_IMAGES_PER_SITE} imágenes por sitio.`, 'error');
            this.clearFileSelection();
            return;
        }
        
        const validFiles = [];
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const maxSize = 5 * 1024 * 1024;
        let invalidCount = 0;
        let skippedCount = 0;
        
        for (let i = 0; i < files.length && validFiles.length < availableSlots; i++) {
            const file = files[i];
            
            if (!allowedTypes.includes(file.type) || file.size > maxSize) {
                invalidCount++;
                continue;
            }
            
            validFiles.push(file);
        }
        
        if (files.length > validFiles.length + invalidCount) {
            skippedCount = files.length - validFiles.length - invalidCount;
        }
        
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
        
        this.currentValidFiles = validFiles;
        
        const hasExistingImages = this.images.length > 0;
        
        this.previewImages = validFiles.map((file, index) => ({
            file: file,
            index: index,
            titulo_alt: '',
            descripcion: '',
            isCover: false,
            order: index
        }));
        
        if (!hasExistingImages && validFiles.length > 0) {
            this.previewImages[0].isCover = true;
        }
        
        this.renderPreviewImages();
        
        previewContainer.style.display = 'block';
        if (clearBtn) clearBtn.style.display = 'inline-block';
    },
    
    renderPreviewImages: function() {
        const selectedList = document.getElementById('selected-images-list');
        if (!selectedList) return;
        
        this.renderCounter++;
        const currentRender = this.renderCounter;
        
        selectedList.innerHTML = '';
        
        if (this.previewImages.length === 0) {
            return;
        }
        
        const sorted = [...this.previewImages].sort((a, b) => a.order - b.order);
        const totalImages = sorted.length;
        
        sorted.forEach((imgData, displayIndex) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (currentRender !== this.renderCounter) {
                    return;
                }
                const imageItem = this.createImagePreviewItem(imgData, displayIndex, totalImages, e.target.result);
                selectedList.appendChild(imageItem);
            };
            reader.onerror = () => {};
            reader.readAsDataURL(imgData.file);
        });
    },
    
    createImagePreviewItem: function(imgData, displayIndex, totalImages, previewUrl) {
        const div = document.createElement('div');
        div.className = `preview-image-item border-2 rounded-md p-3 bg-white ${imgData.isCover ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`;
        
        const hasExistingImages = this.images.length > 0;
        const coverBadge = imgData.isCover ? '<span class="inline-block bg-blue-500 text-white text-xs px-2 py-1 rounded mb-2">PORTADA</span>' : '';
        
        let coverButton = '';
        if (imgData.isCover) {
            if (hasExistingImages) {
                coverButton = `<button type="button" onclick="imagesManager.unsetPreviewCover(${imgData.index})" class="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded">Quitar Portada</button>`;
            }
        } else {
            coverButton = `<button type="button" onclick="imagesManager.setPreviewCover(${imgData.index})" class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded">Marcar como Portada</button>`;
        }
        
        let arrowButtons = '';
        if (totalImages > 1) {
            const isFirst = displayIndex === 0;
            const isLast = displayIndex === totalImages - 1;
            const upDisabled = isFirst ? 'disabled' : '';
            const downDisabled = isLast ? 'disabled' : '';
            const upClass = isFirst ? 'bg-gray-400 cursor-not-allowed' : 'bg-gray-600 hover:bg-gray-700';
            const downClass = isLast ? 'bg-gray-400 cursor-not-allowed' : 'bg-gray-600 hover:bg-gray-700';
            const upOnClick = isFirst ? '' : `onclick="imagesManager.movePreviewImageLeft(${imgData.index})"`;
            const downOnClick = isLast ? '' : `onclick="imagesManager.movePreviewImageRight(${imgData.index})"`;
            
            arrowButtons = `
                <div class="flex gap-2 justify-center mt-2">
                    <button type="button" ${upOnClick} 
                            class="arrow-btn-up ${upClass} text-white px-3 py-1 rounded text-sm" 
                            title="Mover hacia arriba" ${upDisabled}>↑</button>
                    <button type="button" ${downOnClick} 
                            class="arrow-btn-down ${downClass} text-white px-3 py-1 rounded text-sm" 
                            title="Mover hacia abajo" ${downDisabled}>↓</button>
                </div>
            `;
        }
        
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
                        <label class="block text-xs font-medium text-gray-700 mb-1">Título *</label>
                        <input type="text" class="image-title-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                               data-index="${imgData.index}" value="${imgData.titulo_alt || ''}" 
                               placeholder="Título" maxlength="255" required
                               onchange="imagesManager.updatePreviewMetadata(${imgData.index}, 'titulo_alt', this.value)">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Descripción (opcional)</label>
                        <textarea class="image-desc-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                                  data-index="${imgData.index}" rows="2" placeholder="Descripción adicional"
                                  onchange="imagesManager.updatePreviewMetadata(${imgData.index}, 'descripcion', this.value)">${imgData.descripcion || ''}</textarea>
                    </div>
                    ${arrowButtons}
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
        this.previewImages.forEach(img => {
            img.isCover = false;
        });
        
        const imgData = this.previewImages.find(img => img.index === index);
        if (imgData) {
            imgData.isCover = true;
        }
        
        this.renderPreviewImages();
    },
    
    unsetPreviewCover: function(index) {
        const hasExistingImages = this.images.length > 0;
        if (!hasExistingImages) {
            this.showMessage('Debe haber al menos una imagen marcada como portada cuando no hay imágenes cargadas previamente.', 'error');
            return;
        }
        
        const imgData = this.previewImages.find(img => img.index === index);
        if (imgData) {
            imgData.isCover = false;
        }
        
        this.renderPreviewImages();
    },
    
    movePreviewImageLeft: function(imageIndex) {
        const currentImg = this.previewImages.find(img => img.index === imageIndex);
        if (!currentImg) return;
        
        const sorted = [...this.previewImages].sort((a, b) => a.order - b.order);
        const currentSortedIndex = sorted.findIndex(img => img.index === imageIndex);
        
        if (currentSortedIndex <= 0 || currentSortedIndex >= sorted.length) return;
        
        const previousImg = sorted[currentSortedIndex - 1];
        const tempOrder = currentImg.order;
        currentImg.order = previousImg.order;
        previousImg.order = tempOrder;
        
        this.renderPreviewImages();
    },
    
    movePreviewImageRight: function(imageIndex) {
        const currentImg = this.previewImages.find(img => img.index === imageIndex);
        if (!currentImg) return;
        
        const sorted = [...this.previewImages].sort((a, b) => a.order - b.order);
        const currentSortedIndex = sorted.findIndex(img => img.index === imageIndex);
        
        if (currentSortedIndex < 0 || currentSortedIndex >= sorted.length - 1) return;
        
        const nextImg = sorted[currentSortedIndex + 1];
        const tempOrder = currentImg.order;
        currentImg.order = nextImg.order;
        nextImg.order = tempOrder;
        
        this.renderPreviewImages();
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
        this.renderCounter++;
    },
    
    uploadSelectedImages: async function() {
        const files = this.currentValidFiles;
        
        if (!files || files.length === 0) {
            this.showMessage('Por favor seleccione al menos una imagen válida', 'error');
            return;
        }
        
        const currentCount = this.images.length + this.pendingImages.length;
        const availableSlots = this.MAX_IMAGES_PER_SITE - currentCount;
        
        if (availableSlots <= 0) {
            this.showMessage(`Ya ha alcanzado el límite máximo de ${this.MAX_IMAGES_PER_SITE} imágenes por sitio.`, 'error');
            return;
        }
        
        const sortedPreview = [...this.previewImages].sort((a, b) => a.order - b.order);
        const maxToProcess = Math.min(sortedPreview.length, availableSlots);
        
        const hasExistingImages = this.images.length > 0;
        const selectedCover = sortedPreview.find(img => img.isCover);
        
        if (!hasExistingImages && !selectedCover) {
            this.showMessage('Debe seleccionar al menos una imagen como portada cuando no hay imágenes cargadas previamente.', 'error');
            return;
        }
        
        const imagesData = [];
        let coverSet = false;
        
        for (let i = 0; i < maxToProcess; i++) {
            const imgData = sortedPreview[i];
            const tituloAlt = imgData.titulo_alt.trim();
            const descripcion = imgData.descripcion ? imgData.descripcion.trim() : null;
            
            if (!tituloAlt) {
                this.showMessage(`El título es obligatorio para la imagen ${i + 1}`, 'error');
                return;
            }
            
            const isCover = imgData.isCover && !coverSet;
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
            await this.uploadMultipleImages(imagesData);
        } else {
            this.pendingImages = this.pendingImages.concat(imagesData);
            this.savePendingImages();
            this.showMessage(`${imagesData.length} imagen(es) agregada(s) a la cola. Se subirán cuando cree el sitio.`, 'success');
            this.clearFileSelection();
            setTimeout(() => {
                this.updatePendingImagesDisplay();
            }, 100);
        }
    },
    
    savePendingImages: async function() {
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
        
        imagesData.forEach((imgData, index) => {
            formData.append('imagenes', imgData.file);
            formData.append('titulo_alt[]', imgData.titulo_alt);
            if (imgData.descripcion) {
                formData.append('descripcion[]', imgData.descripcion);
            }
            if (imgData.is_cover) {
                formData.append('cover_index', index);
            }
        });
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`, {
                method: 'POST',
                body: formData
            });
            
            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                const text = await response.text();
                this.showMessage(`Error al procesar respuesta del servidor (${response.status}): ${text.substring(0, 200)}`, 'error');
                return;
            }
            
            if (data.success) {
                const coverIndex = imagesData.findIndex(img => img.is_cover);
                if (coverIndex !== -1 && data.images && data.images[coverIndex]) {
                    const coverImageId = data.images[coverIndex].id;
                    await this.setCover(coverImageId, false);
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
        const stored = localStorage.getItem('pending_site_images_meta');
        if (stored) {
            try {
                const pendingData = JSON.parse(stored);
                if (pendingData.length > 0) {
                    this.updatePendingImagesDisplay();
                }
            } catch (e) {
            }
        }
    },
    
    updatePendingImagesDisplay: function() {
        let container = document.getElementById('pending-images-container');
        const imagesSection = document.getElementById('images-section');
        
        if (!imagesSection) {
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
            
            const uploadForm = document.getElementById('upload-image-form');
            const imagesListContainer = document.getElementById('images-list-container');
            
            if (uploadForm && uploadForm.parentElement) {
                uploadForm.parentElement.insertAdjacentElement('afterend', container);
            } else if (imagesListContainer) {
                imagesListContainer.insertAdjacentElement('beforebegin', container);
            } else {
                imagesSection.appendChild(container);
            }
        }
        
        container.style.display = 'block';
        container.className = 'mb-6 p-4 border border-yellow-300 rounded-md bg-yellow-50';
        container.innerHTML = `
            <div id="pending-images-grid" class="space-y-3"></div>
        `;
        
        const grid = document.getElementById('pending-images-grid');
        if (grid) {
            grid.innerHTML = '';
            this.pendingImages.forEach((imgData, index) => {
                if (!imgData.file) {
                    return;
                }
                const reader = new FileReader();
                reader.onload = (e) => {
                    const imageItem = this.createPendingImageItem(imgData, index, e.target.result);
                    grid.appendChild(imageItem);
                };
                reader.onerror = () => {};
                reader.readAsDataURL(imgData.file);
            });
        }
    },
    
    createPendingImageItem: function(imgData, index, previewUrl) {
        const div = document.createElement('div');
        div.className = `pending-image-item border-2 rounded-md p-3 bg-white ${imgData.is_cover ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`;
        
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
                        <label class="block text-xs font-medium text-gray-700 mb-1">Título *</label>
                        <input type="text" class="pending-title-input w-full px-2 py-1 text-sm border border-gray-300 rounded" 
                               value="${imgData.titulo_alt || ''}" 
                               placeholder="Título" maxlength="255" required
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
        this.pendingImages.forEach(img => {
            img.is_cover = false;
        });
        
        if (this.pendingImages[index]) {
            this.pendingImages[index].is_cover = true;
        }
        
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
        if (!this.siteId) return;
        
        try {
            const response = await fetch(`/sitios/${this.siteId}/imagenes`);
            
            if (!response.ok) {
                this.showMessage(`Error al cargar imágenes (${response.status})`, 'error');
                return;
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.images = data.images || [];
                this.renderImages();
            } else {
                this.showMessage(data.error || 'Error al cargar imágenes', 'error');
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
        
        const sortedImages = [...this.images].sort((a, b) => a.orden - b.orden);
        const totalImages = sortedImages.length;
        
        const html = sortedImages.map((img, index) => {
            const isCover = img.es_portada;
            
            let arrowButtons = '';
            if (totalImages > 1) {
                if (index > 0 && index < totalImages - 1) {
                    arrowButtons = `
                        <div class="flex gap-2 justify-center mb-2">
                            <button type="button" onclick="imagesManager.moveImageLeft(${img.id})" 
                                    class="arrow-btn-left bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm" 
                                    title="Mover hacia la izquierda">←</button>
                            <button type="button" onclick="imagesManager.moveImageRight(${img.id})" 
                                    class="arrow-btn-right bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm" 
                                    title="Mover hacia la derecha">→</button>
                        </div>
                    `;
                } else if (index === 0) {
                    arrowButtons = `
                        <div class="flex gap-2 justify-center mb-2">
                            <button type="button" onclick="imagesManager.moveImageRight(${img.id})" 
                                    class="arrow-btn-right bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm" 
                                    title="Mover hacia la derecha">→</button>
                        </div>
                    `;
                } else if (index === totalImages - 1) {
                    arrowButtons = `
                        <div class="flex gap-2 justify-center mb-2">
                            <button type="button" onclick="imagesManager.moveImageLeft(${img.id})" 
                                    class="arrow-btn-left bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm" 
                                    title="Mover hacia la izquierda">←</button>
                        </div>
                    `;
                }
            }
            
            const imageUrl = img.url_publica || '';
            const placeholderSvg = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ccc\' width=\'200\' height=\'200\'/%3E%3Ctext fill=\'%23999\' font-family=\'sans-serif\' font-size=\'14\' x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dominant-baseline=\'middle\'%3EError al cargar%3C/text%3E%3C/svg%3E';
            
            return `
                <div class="image-item ${isCover ? 'cover' : ''}" data-image-id="${img.id}">
                    ${isCover ? '<span class="cover-badge">PORTADA</span>' : ''}
                    <img src="${imageUrl}" alt="${img.titulo_alt || 'Imagen'}" loading="lazy" 
                         onerror="this.onerror=null; this.src='${placeholderSvg}';">
                    <div class="image-info">
                        <p class="text-sm font-medium text-gray-800 truncate" title="${img.titulo_alt || ''}">${img.titulo_alt || 'Sin título'}</p>
                        ${img.descripcion ? `<p class="text-xs text-gray-600 mt-1 truncate" title="${img.descripcion}">${img.descripcion}</p>` : ''}
                    </div>
                    ${arrowButtons}
                    <div class="image-actions">
                        <div class="flex gap-2 justify-center">
                            ${!isCover ? `<button onclick="imagesManager.setCover(${img.id})" class="text-xs bg-blue-500 hover:bg-blue-600 px-2 py-1 rounded" title="Marcar como portada">Portada</button>` : ''}
                            <button onclick="imagesManager.deleteImage(${img.id})" class="text-xs bg-red-500 hover:bg-red-600 px-2 py-1 rounded" title="Eliminar">Eliminar</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    },
    
    moveImageLeft: async function(imageId) {
        if (!this.siteId) return;
        
        const sorted = [...this.images].sort((a, b) => a.orden - b.orden);
        const currentIndex = sorted.findIndex(img => img.id === imageId);
        
        if (currentIndex <= 0) return;
        
        const currentImg = sorted[currentIndex];
        const previousImg = sorted[currentIndex - 1];
        const tempOrder = currentImg.orden;
        currentImg.orden = previousImg.orden;
        previousImg.orden = tempOrder;
        
        this.images.forEach(img => {
            if (img.id === currentImg.id) {
                img.orden = currentImg.orden;
            } else if (img.id === previousImg.id) {
                img.orden = previousImg.orden;
            }
        });
        
        const success = await this.saveImageOrder();
        
        if (success) {
            setTimeout(() => {
                this.loadImages();
            }, 300);
        }
    },
    
    moveImageRight: async function(imageId) {
        if (!this.siteId) return;
        
        const sorted = [...this.images].sort((a, b) => a.orden - b.orden);
        const currentIndex = sorted.findIndex(img => img.id === imageId);
        
        if (currentIndex >= sorted.length - 1) return;
        
        const currentImg = sorted[currentIndex];
        const nextImg = sorted[currentIndex + 1];
        const tempOrder = currentImg.orden;
        currentImg.orden = nextImg.orden;
        nextImg.orden = tempOrder;
        
        this.images.forEach(img => {
            if (img.id === currentImg.id) {
                img.orden = currentImg.orden;
            } else if (img.id === nextImg.id) {
                img.orden = nextImg.orden;
            }
        });
        
        const success = await this.saveImageOrder();
        
        if (success) {
            setTimeout(() => {
                this.loadImages();
            }, 300);
        }
    },
    
    saveImageOrder: async function() {
        if (!this.siteId) return;
        
        const sorted = [...this.images].sort((a, b) => a.orden - b.orden);
        const imageOrders = sorted.map((img, index) => ({
            id: img.id,
            orden: index + 1
        }));
        
        if (imageOrders.length === 0) return;
        
        try {
            const formData = new FormData();
            imageOrders.forEach(order => {
                formData.append(`orden_${order.id}`, order.orden);
            });
            
            const response = await fetch(`/sitios/${this.siteId}/imagenes/reordenar`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    return true;
                } else {
                    this.showMessage(data.error || 'Error al guardar el orden', 'error');
                    return false;
                }
            } else {
                this.showMessage('Error al guardar el orden', 'error');
                return false;
            }
        } catch (error) {
            this.showMessage('Error al guardar el orden: ' + error.message, 'error');
            return false;
        }
    },
    
    setCover: async function(imageId, showConfirm = true) {
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
    
    showMessage: function(message, type) {
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
        
        const duration = (type === 'warning' || type === 'info') ? 5000 : 3000;
        
        setTimeout(() => {
            messageEl.remove();
        }, duration);
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const siteIdInput = document.getElementById('site-id-for-images');
    const siteId = siteIdInput && siteIdInput.value ? parseInt(siteIdInput.value) : null;
    imagesManager.init(siteId);
});
