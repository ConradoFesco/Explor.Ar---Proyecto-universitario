(function(){
  async function loadRoles(){
    try{
      const response = await fetch('/api/users/roles');
      const data = await response.json();
      const rolesContainer = document.getElementById('roles-container');
      if (!rolesContainer) return;
      if (data.roles && Array.isArray(data.roles)){
        rolesContainer.innerHTML = '';
        data.roles.forEach(role => {
          const roleDiv = document.createElement('div');
          roleDiv.className = 'flex items-center mb-2';
          roleDiv.innerHTML = `
            <input type="checkbox" id="role_${role.id}" value="${role.id}" class="role-checkbox h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
            <label for="role_${role.id}" class="ml-2 text-sm text-gray-700">${(role.name||'').charAt(0).toUpperCase() + (role.name||'').slice(1)}</label>
          `;
          rolesContainer.appendChild(roleDiv);
        });
      } else {
        rolesContainer.innerHTML = '<div class="text-sm text-red-500">Error al cargar roles</div>';
      }
    } catch(err){
      const rolesContainer = document.getElementById('roles-container');
      if (rolesContainer) rolesContainer.innerHTML = '<div class="text-sm text-red-500">Error al cargar roles</div>';
    }
  }

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

    const payload = { data_new_user: { name, last_name, mail, password, roles: selectedRoles, active, blocked } };
    try{
      const response = await fetch('/api/users', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(payload) });
      const data = await response.json().catch(()=>({}));
      if (response.ok){
        if (typeof Swal !== 'undefined'){
          Swal.fire({ icon:'success', title:'¡Usuario creado!', text:'El usuario se ha creado correctamente', confirmButtonColor:'#3B82F6', timer:2000, showConfirmButton:false })
            .then(()=> window.location.replace('/users'));
        } else { window.location.replace('/users'); }
      } else {
        if (typeof Swal !== 'undefined') Swal.fire({ icon:'error', title:'Error', text: data.error || 'No se pudo crear el usuario', confirmButtonColor:'#3B82F6' });
      }
    } catch(err){ if (typeof Swal !== 'undefined') Swal.fire({ icon:'error', title:'Error de conexión', text: err.message, confirmButtonColor:'#3B82F6' }); }
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
    loadRoles();
    const form = document.getElementById('createUserForm');
    if (form) form.addEventListener('submit', onSubmit);
    setupConfirmValidation();
  }

  document.addEventListener('DOMContentLoaded', setup);
})();


