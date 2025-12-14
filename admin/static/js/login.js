(function(){
  function setup(){
    const form = document.getElementById('loginForm');
    const msg = document.getElementById('loginMsg');
    if (!form) return;
    form.setAttribute('method','post');
    form.setAttribute('action','/login');
    form.addEventListener('submit', function(e){
      const mail = document.getElementById('mail')?.value?.trim() || '';
      const password = document.getElementById('password')?.value || '';
      if (!mail || !password){
        e.preventDefault();
        if (msg){ msg.textContent='Ingrese correo y contraseña'; msg.classList.remove('hidden'); msg.classList.add('text-red-500'); }
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (mail && !emailRegex.test(mail)){
        e.preventDefault();
        if (typeof Swal !== 'undefined') {
          Swal.fire({ icon:'warning', title:'Email inválido', text:'Ingrese un correo válido', confirmButtonColor:'#3B82F6' });
        } else if (msg){
          msg.textContent='Ingrese un correo válido'; msg.classList.remove('hidden'); msg.classList.add('text-red-500');
        }
      }
    });
  }

  document.addEventListener('DOMContentLoaded', setup);
})();


