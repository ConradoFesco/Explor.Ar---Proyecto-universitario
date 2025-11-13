(function(){
  function openModal(id){ const m=document.getElementById(id); if (m) m.classList.remove('hidden'); }
  window.closeModal = function(id){ const m=document.getElementById(id); if (m) m.classList.add('hidden'); };

  function savePassword(){
    const msg = document.getElementById('passwordMsg');
    const input = document.getElementById('newPassword');
    if (!input || !msg) return;
    const val = (input.value || '').trim();
    if (!val || val.length < 6){
      msg.textContent = 'La contraseña debe tener al menos 6 caracteres';
      msg.classList.remove('hidden');
      msg.classList.remove('text-green-500');
      msg.classList.add('text-red-500');
      return;
    }
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/profile/update_password';
    const i = document.createElement('input'); i.type='hidden'; i.name='new_password'; i.value=val; form.appendChild(i);
    document.body.appendChild(form);
    form.submit();
  }

  function setup(){
    const openBtn = document.getElementById('openPwdModal');
    if (openBtn){ openBtn.addEventListener('click', ()=>{ const msg=document.getElementById('passwordMsg'); if (msg) msg.classList.add('hidden'); const input=document.getElementById('newPassword'); if (input) input.value=''; openModal('passwordModal'); }); }
    const cancelBtn = document.getElementById('cancelModal');
    if (cancelBtn){ cancelBtn.addEventListener('click', ()=> window.closeModal('passwordModal')); }
    const saveBtn = document.getElementById('savePassword');
    if (saveBtn){ saveBtn.addEventListener('click', savePassword); }
  }

  document.addEventListener('DOMContentLoaded', setup);
})();


