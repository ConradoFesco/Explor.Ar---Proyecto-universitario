document.addEventListener('DOMContentLoaded', function(){
  // Inicializar el mapa sin funcionalidad de clic (solo visualización)
  if (typeof mapHandler !== 'undefined'){
    const noClickHandler = function(_coords){};
    mapHandler.initializeMap('map-container', [-34.92, -57.95], 13, noClickHandler);
    mapHandler.loadHistoricSites();
  }
});


