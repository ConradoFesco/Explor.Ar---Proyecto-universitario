document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  const body = document.body;
  if (menuToggle){
    menuToggle.addEventListener('click', function(){
      setTimeout(()=>{
        if (sidebar && sidebar.classList.contains('-translate-x-full')){ body.classList.remove('sidebar-open'); }
        else { body.classList.add('sidebar-open'); }
      }, 10);
    });
  }
  const overlay = document.getElementById('overlay');
  if (overlay){ overlay.addEventListener('click', function(){ body.classList.remove('sidebar-open'); }); }
});


