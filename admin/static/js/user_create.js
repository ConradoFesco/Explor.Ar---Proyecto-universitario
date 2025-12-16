
(function(){

  function validateEmail(mail){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail); }

  async function onSubmit(e){
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const last_name = document.getElementById('last_name').value.trim();
    const mail = document.getElementById('mail').value.trim();
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const selectedRoles = Array.from(document.querySelectorAll('.role-checkbox:checked')).map(cb => parseInt(cb.value, 10));
    const active = document.getElementById('active').checked;
    const blocked = document.getElementById('blocked').checked;

    if (!name || !last_name || !mail || !password || selectedRoles.length === 0){
      if (typeof Swal !== 'undefined') Swal.fire({ icon:'warning', title:'Campos incompletos', text:'Por favor completa todos los campos obligatorios y selecciona al menos un rol', confirmButtonColor:'#3B82F6' });
      return;
    }
    if (password !== confirm_password){ if (typeof Swal !== 'undefined') Swal.fire({ icon:'error', title:'Contraseñas no coinciden', text:'Las contraseñas ingresadas no son iguales', confirmButtonColor:'#3B82F6' }); return; }
    if (password.length < 6){ if (typeof Swal !== 'undefined') Swal.fire({ icon:'warning', title:'Contraseña muy corta', text:'La contraseña debe tener al menos 6 caracteres', confirmButtonColor:'#3B82F6' }); return; }
    if (!validateEmail(mail)){ if (typeof Swal !== 'undefined') Swal.fire({ icon:'warning', title:'Email inválido', text:'Por favor ingresa un email válido', confirmButtonColor:'#3B82F6' }); return; }

    const form = document.getElementById('createUserForm');
    if (form){ form.method = 'POST'; form.action = '/users'; form.submit(); }
  }

  function setupConfirmValidation(){
    const confirm = document.getElementById('confirm_password');
    if (!confirm) return;
    confirm.addEventListener('input', function(){
      const password = document.getElementById('password').value;
      if (this.value && password !== this.value){ this.setCustomValidity('Las contraseñas no coinciden'); this.classList.add('border-red-500'); }
      else { this.setCustomValidity(''); this.classList.remove('border-red-500'); }
    });
  }

  function setup(){
    const form = document.getElementById('createUserForm');
    if (form) form.addEventListener('submit', onSubmit);
    setupConfirmValidation();
  }

  document.addEventListener('DOMContentLoaded', setup);
})();


