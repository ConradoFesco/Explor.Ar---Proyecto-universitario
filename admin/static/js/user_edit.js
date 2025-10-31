(function(){
  let originalUserData = null;

  function getConfig(){
    if (!window.USER_EDIT_CONFIG) throw new Error('USER_EDIT_CONFIG no definido');
    return window.USER_EDIT_CONFIG;
  }

  async function loadUserData(){
    const { userId } = getConfig();
    try {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
      const userData = await response.json();
      originalUserData = userData;
      populateForm(userData);
      const loading = document.getElementById('loading-state'); if (loading) loading.classList.add('hidden');
      const form = document.getElementById('editUserForm'); if (form) form.classList.remove('hidden');
    } catch (err){
      console.error('Error cargando datos del usuario:', err);
      showError(err.message);
    }
  }

  function populateForm(userData){
    setValue('name', userData.name || '');
    setValue('last_name', userData.last_name || '');
    setValue('mail', userData.mail || '');
    setChecked('active', !!userData.active);
    setChecked('blocked', !!userData.blocked);
    setText('user-id', userData.id || '-');
    if (userData.created_at){
      try {
        const date = new Date(userData.created_at);
        setText('user-created-at', date.toLocaleString('es-ES', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }));
      } catch (_e){ setText('user-created-at', userData.created_at); }
    } else {
      setText('user-created-at','N/A');
    }
    populateRoles(userData.available_roles || [], userData.current_roles || []);
  }

  function populateRoles(availableRoles, currentRoles){
    const rolesContainer = document.getElementById('roles-container');
    if (!rolesContainer) return;
    if (availableRoles.length === 0){
      rolesContainer.innerHTML = '<div class="text-sm text-red-500">No hay roles disponibles</div>';
      return;
    }
    rolesContainer.innerHTML = '';
    const currentRoleIds = currentRoles.map(r => r.id);
    availableRoles.forEach(role => {
      const roleDiv = document.createElement('div');
      roleDiv.className = 'flex items-center mb-2';
      const isChecked = currentRoleIds.includes(role.id);
      roleDiv.innerHTML = `
        <input type="checkbox" id="role_${role.id}" value="${role.id}" ${isChecked ? 'checked' : ''} class="role-checkbox h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
        <label for="role_${role.id}" class="ml-2 text-sm text-gray-700">${capitalize(role.name)}</label>
      `;
      rolesContainer.appendChild(roleDiv);
    });
  }

  function showError(message){
    const loading = document.getElementById('loading-state'); if (loading) loading.classList.add('hidden');
    const errorState = document.getElementById('error-state'); if (errorState) errorState.classList.remove('hidden');
    setText('error-message', message);
  }

  function validateForm(){
    const name = (document.getElementById('name')?.value || '').trim();
    const lastName = (document.getElementById('last_name')?.value || '').trim();
    const email = (document.getElementById('mail')?.value || '').trim();
    const selectedRoles = Array.from(document.querySelectorAll('.role-checkbox:checked'));
    const isBlocked = !!document.getElementById('blocked')?.checked;

    if (!name){ return warn('Nombre requerido','El nombre no puede estar vacío'); }
    if (!lastName){ return warn('Apellido requerido','El apellido no puede estar vacío'); }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)){ return warn('Email inválido','Por favor ingresa un email válido'); }
    if (selectedRoles.length === 0){ return warn('Roles requeridos','Debe seleccionar al menos un rol'); }

    const hasAdminRole = selectedRoles.some(cb => (cb.nextElementSibling?.textContent || '').toLowerCase().includes('admin'));
    if (hasAdminRole && isBlocked){ return error('Acción no permitida','No se puede bloquear a un usuario con rol de Administrador'); }
    return true;
  }

  function collectFormData(){
    return {
      name: document.getElementById('name')?.value,
      last_name: document.getElementById('last_name')?.value,
      mail: document.getElementById('mail')?.value,
      active: !!document.getElementById('active')?.checked,
      blocked: !!document.getElementById('blocked')?.checked,
    };
  }

  function computeChanges(current, original){
    const changed = {};
    Object.keys(current).forEach(k => { if (current[k] !== original[k]) changed[k] = current[k]; });
    return changed;
  }

  function getSelectedRoleIds(){
    return Array.from(document.querySelectorAll('.role-checkbox:checked')).map(cb => parseInt(cb.value, 10)).sort();
  }

  function getOriginalRoleIds(){
    return (originalUserData.current_roles || []).map(r => r.id).sort();
  }

  async function handleSubmit(e){
    e.preventDefault();
    if (!validateForm()) return;
    const { userId, currentUserId } = getConfig();
    const currentData = collectFormData();
    const changedFields = computeChanges(currentData, originalUserData || {});
    const originalRoleIds = getOriginalRoleIds();
    const currentRoleIds = getSelectedRoleIds();
    const rolesChanged = JSON.stringify(originalRoleIds) !== JSON.stringify(currentRoleIds);

    if (Object.keys(changedFields).length === 0 && !rolesChanged){
      return info('Sin cambios','No hay cambios para guardar');
    }

    try {
      if (Object.keys(changedFields).length > 0){
        const resp = await fetch(`/api/users/${userId}`, {
          method:'PUT', headers:{ 'Content-Type':'application/json' },
          body: JSON.stringify({ data_user:{ id: currentUserId }, data_new: changedFields })
        });
        if (!resp.ok){ const data = await resp.json(); throw new Error(data.error || 'Error al actualizar usuario'); }
      }

      if (rolesChanged){
        const resp = await fetch(`/api/users/${userId}/roles`, {
          method:'PUT', headers:{ 'Content-Type':'application/json' },
          body: JSON.stringify({ data_user:{ id: currentUserId }, role_ids: currentRoleIds })
        });
        if (!resp.ok){ const data = await resp.json(); throw new Error(data.error || 'Error al actualizar roles'); }
      }

      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'success', title:'¡Actualizado!', text:'Usuario actualizado correctamente', confirmButtonColor:'#3B82F6', timer:2000, showConfirmButton:false })
          .then(()=> window.location.replace('/users'));
      } else {
        alert('Usuario actualizado'); window.location.replace('/users');
      }
    } catch (err){
      if (typeof Swal !== 'undefined'){
        Swal.fire({ icon:'error', title:'Error de conexión', text: err.message, confirmButtonColor:'#3B82F6' });
      } else { alert('Error: ' + err.message); }
    }
  }

  // Helpers UI
  function setValue(id, val){ const el = document.getElementById(id); if (el) el.value = val; }
  function setChecked(id, checked){ const el = document.getElementById(id); if (el) el.checked = checked; }
  function setText(id, text){ const el = document.getElementById(id); if (el) el.textContent = text; }
  function capitalize(s){ return (s||'').charAt(0).toUpperCase() + (s||'').slice(1); }
  function warn(title, text){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'warning', title, text, confirmButtonColor:'#3B82F6' }); } return false; }
  function error(title, text){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'error', title, text, confirmButtonColor:'#3B82F6' }); } return false; }
  function info(title, text){ if (typeof Swal !== 'undefined'){ Swal.fire({ icon:'info', title, text, confirmButtonColor:'#3B82F6' }); } return false; }

  function init(){
    const form = document.getElementById('editUserForm');
    if (form){ form.addEventListener('submit', handleSubmit); }
    loadUserData();
  }

  document.addEventListener('DOMContentLoaded', init);
})();


