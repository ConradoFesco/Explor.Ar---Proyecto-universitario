(function(){
  async function handleSubmit(e){
    e.preventDefault();
    const mail = document.getElementById('mail')?.value || '';
    const password = document.getElementById('password')?.value || '';
    const loginMsg = document.getElementById('loginMsg');
    if (loginMsg){ loginMsg.classList.add('hidden'); }
    try{
      const res = await fetch('/api/login', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify({ mail, password }) });
      const data = await res.json().catch(()=>({}));
      if (res.ok){ window.location.href = '/home'; return; }
      if (loginMsg){
        loginMsg.textContent = data.error || 'Credenciales inválidas';
        loginMsg.classList.remove('hidden');
        loginMsg.classList.remove('text-green-500');
        loginMsg.classList.add('text-red-500');
      }
    } catch(_e){
      if (loginMsg){
        loginMsg.textContent = 'Ocurrió un error al conectar con el servidor';
        loginMsg.classList.remove('hidden');
        loginMsg.classList.remove('text-green-500');
        loginMsg.classList.add('text-red-500');
      }
    }
  }

  function setup(){
    const form = document.getElementById('loginForm');
    if (form){ form.addEventListener('submit', handleSubmit); }
  }

  document.addEventListener('DOMContentLoaded', setup);
})();


