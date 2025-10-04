// Verificamos que Leaflet esté disponible antes de continuar
if (typeof L === 'undefined') {
    console.error('Leaflet no está cargado. Asegúrate de incluir la librería Leaflet antes de este script.');
}

// Creamos un objeto global que contiene nuestras funciones de mapa
// Esto permite que otros scripts accedan a las funciones sin usar módulos ES6
window.mapHandler = {
    map: null, // Variable para guardar la instancia del mapa de Leaflet

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
    }
};