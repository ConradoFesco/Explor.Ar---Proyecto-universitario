// Verificamos que Leaflet esté disponible antes de continuar
if (typeof L === 'undefined') {
    console.error('Leaflet no está cargado. Asegúrate de incluir la librería Leaflet antes de este script.');
}

// Creamos un objeto global que contiene nuestras funciones de mapa
// Esto permite que otros scripts accedan a las funciones sin usar módulos ES6
window.mapHandler = {
    map: null, // Variable para guardar la instancia del mapa de Leaflet
    markers: [], // Array para guardar los marcadores de sitios históricos

    // Función principal para inicializar el mapa
    initializeMap: function(containerId, initialCoords, initialZoom, onClickCallback) {
        // Verificamos que Leaflet esté disponible
        if (typeof L === 'undefined') {
            console.error('Leaflet no está disponible. No se puede inicializar el mapa.');
            return;
        }

        // 1. Creamos la instancia del mapa de Leaflet
        // containerId: ID del div HTML donde se mostrará el mapa
        // setView: establece la posición inicial y el nivel de zoom
        this.map = L.map(containerId).setView(initialCoords, initialZoom);

        // 2. Configuramos la capa de tiles (imágenes del mapa) de OpenStreetMap
        // Los tiles son las imágenes que forman el mapa
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors' // Atribución requerida por OpenStreetMap
        }).addTo(this.map); // Agregamos la capa al mapa

        // 3. Configuramos el evento de clic en el mapa
        this.map.on('click', function(e) {
            // e.latlng contiene las coordenadas (latitud y longitud) del punto donde se hizo clic
            // Llamamos a la función callback que nos pasaron con las coordenadas
            onClickCallback(e.latlng);
        });
    },

    // Función para cargar sitios históricos desde el backend
    loadHistoricSites: async function() {
        try {
            const response = await fetch('/api/HistoricSite_Routes/map');
            if (!response.ok) {
                throw new Error('Error al cargar sitios históricos');
            }
            const data = await response.json();
            
            // El backend devuelve {sites: [...], pagination: {...}}
            const sites = data.sites || [];
            
            // Limpiar marcadores existentes
            this.clearMarkers();
            
            // Crear marcadores para cada sitio
            sites.forEach(site => {
                this.createSiteMarker(site);
            });
            
            console.log(`${sites.length} sitios históricos cargados en el mapa`);
        } catch (error) {
            console.error('Error cargando sitios históricos:', error);
        }
    },

    // Función para crear un marcador de sitio histórico
    createSiteMarker: function(site) {
        if (!this.map) {
            console.error('El mapa no está inicializado');
            return;
        }

        // Crear marcador
        const marker = L.marker([site.latitude, site.longitude]).addTo(this.map);
        
        // Crear contenido del popup
        const popupContent = `
            <div class="site-popup">
                <h4 class="site-popup-title">${site.name}</h4>
                <p class="site-popup-description">${site.brief_description}</p>
                <div class="site-popup-details">
                    <p><strong>Ciudad:</strong> ${site.name_city || 'No especificada'}</p>
                    <p><strong>Provincia:</strong> ${site.name_province || 'No especificada'}</p>
                    ${site.year_inauguration ? `<p><strong>Año:</strong> ${site.year_inauguration}</p>` : ''}
                </div>
            </div>
        `;
        
        // Agregar popup al marcador
        marker.bindPopup(popupContent);
        
        // Guardar referencia del marcador
        this.markers.push(marker);
        
        return marker;
    },

    // Función para limpiar todos los marcadores
    clearMarkers: function() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    },

    // Función para centrar el mapa en un sitio específico
    centerOnSite: function(site) {
        if (this.map && site.latitude && site.longitude) {
            this.map.setView([site.latitude, site.longitude], 15);
        }
    }
};