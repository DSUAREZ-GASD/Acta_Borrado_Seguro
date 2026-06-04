document.addEventListener('DOMContentLoaded', function() {
    // ==========================================
    // 1. MANEJO DE MENSAJES FLASH (Existente)
    // ==========================================
    const flashMessages = document.querySelectorAll('.flash-mensajes');
    flashMessages.forEach(function(mensaje) {
        Swal.fire({
            icon: mensaje.dataset.icon || 'info',
            title: 'Notificación',
            text: mensaje.textContent,
            showConfirmButton: false,
            timer: 3000
        }).then(function() {
            mensaje.remove();
        });
    });

    // ==========================================
    // 2. ALERTA DE REEMPLAZO DE IMÁGENES (Nueva)
    // ==========================================
    // Buscamos todos los inputs de archivo dentro de la estructura de formularios
    const inputsImagen = document.querySelectorAll('.form-group-imagen input[type="file"]');

    inputsImagen.forEach(function(input) {
        // Guardamos una bandera para saber si el contenedor ya tiene una imagen previa guardada
        // Esto lo detectamos buscando si existe la clase o el texto de "Evidencia custodiada" en el mismo bloque
        const contenedorPadre = input.closest('.form-group-imagen');
        const tieneImagenPrevia = contenedorPadre ? contenedorPadre.querySelector('img') : null;

        if (tieneImagenPrevia) {
            // Variable para almacenar el último archivo válido seleccionado o vacío si es el inicial
            let ultimoArchivoValido = null;

            input.addEventListener('click', function(e) {
                // Capturamos el estado justo antes de que se abra el explorador de archivos
                ultimoArchivoValido = input.files[0];
            });

            input.addEventListener('change', function(e) {
                // Si el usuario cancela la selección y no hay archivo nuevo, no hacemos nada
                if (input.files.length === 0) return;

                const nombreArchivoNuevo = input.files[0].name;

                // Detenemos temporalmente el flujo para pedir confirmación
                e.preventDefault(); 

                Swal.fire({
                    title: '¿Deseas reemplazar esta evidencia?',
                    text: `Estás a punto de sustituir la imagen actual por: "${nombreArchivoNuevo}". Esta acción no se puede deshacer de forma automática.`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, reemplazar',
                    cancelButtonText: 'Cancelar',
                    allowOutsideClick: false
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Confirmado: Mostramos un pequeño feedback visual de éxito temporal
                        Swal.fire({
                            icon: 'success',
                            title: 'Imagen preparada',
                            text: 'El nuevo archivo se cargará cuando guardes o actualices el equipo.',
                            timer: 2000,
                            showConfirmButton: false
                        });
                    } else {
                        // Cancelado: Revertimos el input a su archivo anterior o lo vaciamos
                        if (ultimoArchivoValido) {
                            // Si ya había seleccionado un archivo modificado antes en esta sesión
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(ultimoArchivoValido);
                            input.files = dataTransfer.files;
                        } else {
                            // Si estaba la foto original de la BD intacta, limpiamos el input
                            input.value = '';
                        }
                    }
                });
            });
        }
    });
});