(function(){
  let originalUserData = null;

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

  function handleSubmit(e){
    if (!validateForm()){
      e.preventDefault();
      return false;
    }
    return true;
  }

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
    const loading = document.getElementById('loading-state'); if (loading) loading.classList.add('hidden');
    const frm = document.getElementById('editUserForm'); if (frm) frm.classList.remove('hidden');
  }

  document.addEventListener('DOMContentLoaded', init);
})();


