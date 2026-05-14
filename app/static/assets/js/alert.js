document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-mensajes');
    flashMessages.forEach(function(mensaje) {
        Swal.fire({
            icon: mensaje.dataset.icon || 'info',
            title: 'Mensaje',
            text: mensaje.textContent,
            showConfirmButton: false,
            timer: 3000
        }).then(function() {
            // Eliminar el mensaje flash del DOM
            mensaje.remove();
        });
    });
});