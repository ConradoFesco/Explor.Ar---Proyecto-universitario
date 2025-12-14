document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('form button[type="submit"]').forEach(button => {
    const form = button.closest('form');
    if (!form) return;
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const flagName = this.closest('tr').querySelector('td:first-child span')?.textContent || '';
      const desired = (this.querySelector('input[name="enabled"]')?.value || '0') === '1';
      const actionText = desired ? 'activar' : 'desactivar';
      const msgInput = this.querySelector('input[name="message"]');
      const msg = (msgInput?.value || '').trim();
      Swal.fire({
        title: '¿Confirmar cambio?',
        html: `¿Deseas ${actionText} <strong>${flagName}</strong>?${msg ? `<br/><small>Mensaje: ${msg.substring(0,80)}${msg.length>80?'…':''}</small>` : ''}`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3B82F6',
        cancelButtonColor: '#6B7280',
        confirmButtonText: 'Sí, confirmar',
        cancelButtonText: 'Cancelar'
      }).then((result)=>{
        if (!result.isConfirmed) return;
        Swal.fire({ title:'Actualizando...', allowOutsideClick:false, didOpen: ()=> Swal.showLoading() });
        form.submit();
      });
    });
  });

  document.querySelectorAll('.js-edit-flag-message').forEach(btn => {
    btn.addEventListener('click', function(){
      const flagId = this.getAttribute('data-flag-id');
      const flagName = this.getAttribute('data-flag-name') || '';
      const currentMsg = this.getAttribute('data-current-message') || '';
      Swal.fire({
        title: 'Mensaje de mantenimiento',
        input: 'text',
        inputValue: currentMsg,
        inputAttributes: { maxlength: 255 },
        showCancelButton: true,
        confirmButtonText: 'Guardar',
        cancelButtonText: 'Cancelar',
        preConfirm: (value)=>{
          if (value && value.length > 255) {
            Swal.showValidationMessage('El mensaje no puede superar los 255 caracteres');
            return false;
          }
          return value;
        }
      }).then(res => {
        if (!res.isConfirmed) return;
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/flags/${flagId}/message`;
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'message';
        input.value = res.value || '';
        form.appendChild(input);
        document.body.appendChild(form);
        Swal.fire({ title:'Guardando...', allowOutsideClick:false, didOpen: ()=> Swal.showLoading() });
        form.submit();
      });
    });
  });
});


