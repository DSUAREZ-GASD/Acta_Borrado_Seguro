$(document).ready(function() {
    $('#equiposTable').DataTable({
      responsive: true,
      paging: true,
      searching: true,
      ordering: true,
      language: {
        url: 'https://cdn.datatables.net/plug-ins/1.11.5/i18n/Spanish.json' // URL corregida
      }
    });
  });