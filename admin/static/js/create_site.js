// IMPORTANTE: Este script debe cargarse DESPUÉS de Leaflet y map_handler.js
// Asegúrate de incluir en tu HTML:
// 1. <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
// 2. <script src="static/js/map_handler.js"></script>
// 3. <script src="static/js/create_site.js"></script>

// Esperamos a que el documento HTML esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {

    // Función que se ejecuta cuando el usuario hace clic en el mapa
    const handleMapClick = function(coords) {
        // coords es un objeto que contiene las coordenadas del clic
        // coords.lat = latitud, coords.lng = longitud
        console.log("Coordenadas seleccionadas:", coords);

        // Actualizar los campos del formulario con las coordenadas
        updateFormCoordinates(coords);
        
        // Obtener información de ubicación (ciudad y provincia) usando geocodificación inversa
        getLocationInfo(coords);
        
        // Mostrar mensaje de confirmación en consola (sin modal)
        console.log("Ubicación actualizada en el formulario");
    };


    // Verificamos que mapHandler esté disponible
    if (typeof mapHandler === 'undefined') {
        console.error('mapHandler no está disponible. Verifica que map_handler.js se haya cargado correctamente.');
        return;
    }


    // Inicializamos el mapa con los parámetros especificados
    // Parámetros:
    // - 'map-container': ID del div HTML donde se mostrará el mapa
    // - [-34.92, -57.95]: Coordenadas iniciales (La Plata, Argentina)
    // - 13: Nivel de zoom inicial (1-18, donde 18 es el más cercano)
    // - handleMapClick: Función que se ejecutará cuando se haga clic en el mapa
    mapHandler.initializeMap('map-container', [-34.92, -57.95], 13, handleMapClick);


    // Función para actualizar las coordenadas en el formulario
    function updateFormCoordinates(coords) {
        const latInput = document.getElementById('latitud');
        const lngInput = document.getElementById('longitud');
        
        if (latInput) latInput.value = coords.lat.toFixed(6);
        if (lngInput) lngInput.value = coords.lng.toFixed(6);
    }

    // Función para obtener información de ubicación usando geocodificación inversa
    function getLocationInfo(coords) {
        // Usar Nominatim (OpenStreetMap) para geocodificación inversa
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.lat}&lon=${coords.lng}&zoom=10&addressdetails=1`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Datos de geocodificación:', data);
                
                const ciudadInput = document.getElementById('ciudad');
                const provinciaInput = document.getElementById('provincia');
                
                if (data.address) {
                    // Intentar obtener la ciudad
                    let ciudad = data.address.city || 
                               data.address.town || 
                               data.address.village || 
                               data.address.municipality ||
                               data.address.suburb ||
                               '';
                    
                    // Intentar obtener la provincia/estado
                    let provincia = data.address.state || 
                                  data.address.region || 
                                  data.address.province ||
                                  '';
                    
                    if (ciudadInput) ciudadInput.value = ciudad;
                    if (provinciaInput) provinciaInput.value = provincia;
                }
            })
            .catch(error => {
                console.error('Error en geocodificación inversa:', error);
                // Si falla, dejar los campos vacíos
                const ciudadInput = document.getElementById('ciudad');
                const provinciaInput = document.getElementById('provincia');
                if (ciudadInput) ciudadInput.value = '';
                if (provinciaInput) provinciaInput.value = '';
            });
    }

    // Función para cargar estados desde el backend
    function loadEstados() {
        const url = '/api/state_routes';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const estadoSelect = document.getElementById('estado');
                if (estadoSelect && Array.isArray(data)) {
                    // Limpiar opciones existentes (excepto la primera)
                    estadoSelect.innerHTML = '<option value="">Seleccione un estado...</option>';
                    
                    // Agregar opciones de estados
                    data.forEach(estado => {
                        const option = document.createElement('option');
                        option.value = estado.id;
                        option.textContent = estado.state; // Usar 'state' según el modelo
                        estadoSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error cargando estados:', error);
            });
    }

    // Función para cargar categorías desde el backend
    function loadCategorias() {
        const url = '/api/category_routes';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const categoriaSelect = document.getElementById('categoria');
                if (categoriaSelect && Array.isArray(data)) {
                    // Limpiar opciones existentes (excepto la primera)
                    categoriaSelect.innerHTML = '<option value="">Seleccione una categoría...</option>';
                    
                    // Agregar opciones de categorías
                    data.forEach(categoria => {
                        const option = document.createElement('option');
                        option.value = categoria.id;
                        option.textContent = categoria.name; // Usar 'name' según el modelo
                        categoriaSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error cargando categorías:', error);
            });
    }

    // Función para limpiar el formulario
    window.clearForm = function() {
        const form = document.getElementById('site-form');
        if (form) {
            form.reset();
            // Limpiar campos de solo lectura
            const latInput = document.getElementById('latitud');
            const lngInput = document.getElementById('longitud');
            const ciudadInput = document.getElementById('ciudad');
            const provinciaInput = document.getElementById('provincia');
            
            if (latInput) latInput.value = '';
            if (lngInput) lngInput.value = '';
            if (ciudadInput) ciudadInput.value = '';
            if (provinciaInput) provinciaInput.value = '';
            
            // Limpiar errores visuales
            clearFieldErrors();
        }
    };

    // Función para validar campos requeridos
    function validateRequiredFields() {
        const requiredFields = [
            { id: 'nombre', message: 'El nombre es requerido' },
            { id: 'descripcion_breve', message: 'La descripción breve es requerida' },
            { id: 'estado', message: 'Debe seleccionar un estado' },
            { id: 'categoria', message: 'Debe seleccionar una categoría' }
        ];
        
        let isValid = true;
        
        // Limpiar errores anteriores
        clearFieldErrors();
        
        requiredFields.forEach(field => {
            const input = document.getElementById(field.id);
            const errorDiv = document.getElementById(field.id + '-error');
            
            if (!input.value.trim()) {
                // Marcar campo como error
                input.classList.add('field-error');
                if (errorDiv) {
                    errorDiv.classList.add('show');
                }
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Función para limpiar errores de campos
    function clearFieldErrors() {
        const errorFields = document.querySelectorAll('.field-error');
        const errorMessages = document.querySelectorAll('.error-message');
        
        errorFields.forEach(field => {
            field.classList.remove('field-error');
        });
        
        errorMessages.forEach(message => {
            message.classList.remove('show');
        });
    }
    
    // Función para mostrar mensaje de éxito
    function showSuccessMessage() {
        const successDiv = document.getElementById('success-message');
        if (successDiv) {
            successDiv.classList.add('show');
            // Ocultar después de 5 segundos
            setTimeout(() => {
                successDiv.classList.remove('show');
            }, 5000);
        }
    }
    
    // Función para manejar el envío del formulario
    function handleFormSubmit(event) {
        event.preventDefault();
        
        // Validar que el usuario esté logueado
        if (!window.currentUser || !window.currentUser.id) {
            alert('Error: No se pudo obtener la información del usuario. Por favor, inicie sesión nuevamente.');
            window.location.href = '/';
            return;
        }
        
        // Validar campos requeridos
        if (!validateRequiredFields()) {
            // Hacer scroll al primer campo con error
            const firstError = document.querySelector('.field-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
            return;
        }
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        console.log('Datos del formulario:', data);
        
        // Preparar los datos según la estructura esperada por el backend
        const requestData = {
            data_site: {
                name: data.nombre,
                brief_description: data.descripcion_breve,
                complete_description: data.descripcion_completa || null,
                latitude: parseFloat(data.latitud),
                longitude: parseFloat(data.longitud),
                year_inauguration: data.año_inauguración || null,
                id_estado: parseInt(data.estado),
                id_category: parseInt(data.categoria),
                visible: true, // Por defecto visible
                id_ciudad: 1 // TODO: Obtener el ID de ciudad basado en la geocodificación
            },
            data_user: {
                id_user: window.currentUser ? window.currentUser.id : null
            }
        };
        
        console.log('Datos preparados para el backend:', requestData);
        
        // Enviar datos al backend
        sendDataToBackend(requestData);
    }
    
    // Función para enviar datos al backend
    function sendDataToBackend(data) {
        const submitButton = document.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        // Mostrar estado de carga
        submitButton.textContent = 'Guardando...';
        submitButton.disabled = true;
        
        fetch('/api/HistoricSite_Routes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Error en el servidor');
                });
            }
            return response.json();
        })
        .then(result => {
            console.log('Sitio histórico creado exitosamente:', result);
            showSuccessMessage();
            clearForm();
        })
        .catch(error => {
            console.error('Error al crear el sitio histórico:', error);
            showErrorMessage(error.message);
        })
        .finally(() => {
            // Restaurar botón
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
    }
    
    // Función para mostrar mensaje de error
    function showErrorMessage(message) {
        // Crear o actualizar mensaje de error
        let errorDiv = document.getElementById('error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'error-message';
            errorDiv.className = 'form-error';
            
            // Insertar antes del formulario
            const form = document.getElementById('site-form');
            form.parentNode.insertBefore(errorDiv, form);
        }
        
        errorDiv.textContent = `Error: ${message}`;
        errorDiv.classList.add('show');
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorDiv.classList.remove('show');
        }, 5000);
    }

    // Configurar el evento de envío del formulario
    const form = document.getElementById('site-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Cargar datos iniciales
    loadEstados();
    loadCategorias();
    
    // Agregar event listeners para limpiar errores al escribir
    const requiredFields = ['nombre', 'descripcion_breve', 'estado', 'categoria'];
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                // Limpiar error visual cuando el usuario empiece a escribir
                this.classList.remove('field-error');
                const errorDiv = document.getElementById(fieldId + '-error');
                if (errorDiv) {
                    errorDiv.classList.remove('show');
                }
            });
        }
    });

});