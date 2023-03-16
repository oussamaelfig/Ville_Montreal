$(function () {
    $('#search_btn').click(function () {
        var start_date = $('#start_date').val();
        var end_date = $('#end_date').val();
        $.ajax({
            url: '/contrevenants',
            data: {
                du: start_date,
                au: end_date
            },
            success: function (data) {
                displayResults(data);
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    });
});

function displayResults(data) {
    // Create table with ID
    var $table = $('<table>').attr('id', 'resultsTable').addClass('table');
    var $thead = $('<thead>').appendTo($table);
    var $tr = $('<tr>').appendTo($thead);
    $('<th>').text('Nom de l’établissement').appendTo($tr);
    $('<th>').text('Nombre de contraventions').appendTo($tr);
    var $tbody = $('<tbody>').appendTo($table);
    $.each(data, function (index, row) {
        var $tr = $('<tr>').appendTo($tbody);
        $('<td>').text(row.etablissement).appendTo($tr);
        $('<td>').text(row.nb_contraventions).appendTo($tr);
    });

    // Destroy any existing DataTable instance before creating a new one
    if ($.fn.DataTable.isDataTable('#resultsTable')) {
        $('#resultsTable').DataTable().destroy();
    }

    // Append the table to the results div and initialize DataTables
    $('#results').empty().append($table);
    $('#resultsTable').DataTable({
        paging: true,
        lengthChange: true,
        searching: false,
        ordering: true,
        info: true,
        autoWidth: false,
        pageLength: 10,
        responsive: true,
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.11.5/i18n/French.json'
        }
    });
}
