document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('form button[type="submit"]').forEach(button => {
    const form = button.closest('form');
    if (!form) return;
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const flagName = this.closest('tr').querySelector('td:first-child span')?.textContent || '';
      const currentStatus = button.textContent.trim();
      const newStatus = currentStatus === 'ON' ? 'OFF' : 'ON';
      Swal.fire({
        title: '¿Confirmar cambio?',
        html: `¿Deseas cambiar el estado de <strong>${flagName}</strong> a <strong>${newStatus}</strong>?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3B82F6',
        cancelButtonColor: '#6B7280',
        confirmButtonText: 'Sí, cambiar',
        cancelButtonText: 'Cancelar'
      }).then((result)=>{
        if (!result.isConfirmed) return;
        Swal.fire({ title:'Actualizando...', allowOutsideClick:false, didOpen: ()=> Swal.showLoading() });
        form.submit();
      });
    });
  });
});


