if (typeof L === 'undefined') {
    console.error('Leaflet no está cargado. Asegúrate de incluir la librería Leaflet antes de este script.');
}

window.mapHandler = {
    map: null,
    markers: [],

    initializeMap: function(containerId, initialCoords, initialZoom, onClickCallback) {
        if (typeof L === 'undefined') {
            console.error('Leaflet no está disponible. No se puede inicializar el mapa.');
            return;
        }

        this.map = L.map(containerId).setView(initialCoords, initialZoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(this.map);

        this.map.on('click', function(e) {
            onClickCallback(e.latlng);
        });
    },

    loadHistoricSites: function() {
        const sites = Array.isArray(window.SITES_FOR_MAP) ? window.SITES_FOR_MAP : [];
        this.clearMarkers();
        sites.forEach(site => { this.createSiteMarker(site); });
    },

    createSiteMarker: function(site) {
        if (!this.map) {
            console.error('El mapa no está inicializado');
            return null;
        }
        if (!site) return null;
        const lat = Number.parseFloat(site.latitude);
        const lng = Number.parseFloat(site.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
            return null;
        }

        const marker = L.marker([lat, lng]).addTo(this.map);
        
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
        
        marker.bindPopup(popupContent);
        
        this.markers.push(marker);
        
        return marker;
    },

    clearMarkers: function() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    },

    centerOnSite: function(site) {
        const lat = Number.parseFloat(site?.latitude);
        const lng = Number.parseFloat(site?.longitude);
        if (this.map && Number.isFinite(lat) && Number.isFinite(lng)) {
            this.map.setView([lat, lng], 15);
        }
    }
};