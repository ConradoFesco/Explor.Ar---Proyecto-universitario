(function(){
  function openModal(id){ const m=document.getElementById(id); if (m) m.classList.remove('hidden'); }
  window.closeModal = function(id){ const m=document.getElementById(id); if (m) m.classList.add('hidden'); };

  async function savePassword(){
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
    try{
      const res = await fetch('/profile/update_password', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify({ new_password: val }) });
      const data = await res.json().catch(()=>({}));
      if (res.ok || data.message){
        msg.textContent = data.message || 'Contraseña actualizada';
        msg.classList.remove('hidden');
        msg.classList.remove('text-red-500');
        msg.classList.add('text-green-500');
        setTimeout(()=>{ window.location.href = '/profile'; }, 1500);
      } else {
        msg.textContent = data.error || 'Error al actualizar contraseña';
        msg.classList.remove('hidden');
        msg.classList.remove('text-green-500');
        msg.classList.add('text-red-500');
      }
    } catch(_e){
      msg.textContent = 'Error al actualizar contraseña';
      msg.classList.remove('hidden');
      msg.classList.remove('text-green-500');
      msg.classList.add('text-red-500');
    }
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


