document.getElementById('logout-button').addEventListener('click', function() {
    fetch('/auth/logout', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => {
        if (response.ok) {
            localStorage.removeItem('access_token');
            window.location.href = '/auth/login';
        } else {
            alert('Error al cerrar sesión');
        }
    });
});