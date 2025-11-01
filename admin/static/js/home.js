document.addEventListener('DOMContentLoaded', function(){
  // Inicializar el mapa sin funcionalidad de clic (solo visualización)
  if (typeof mapHandler !== 'undefined'){
    const noClickHandler = function(_coords){};
    mapHandler.initializeMap('map-container', [-34.92, -57.95], 13, noClickHandler);
    const sites = Array.isArray(window.SITES_FOR_MAP) ? window.SITES_FOR_MAP : [];
    sites.forEach(s => mapHandler.createSiteMarker(s));
  }
});


