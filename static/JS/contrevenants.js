$(document).ready(function () {
    loadEtablissements();

    $('#search-button').on('click', function () {
        const etablissement = $('#etablissement-select').val();
        fetchInfractions(etablissement);
    });
});

function formatDate(dateStr) {
    if (dateStr.length === 8) {
        const year = dateStr.substr(0, 4);
        const month = dateStr.substr(4, 2);
        const day = dateStr.substr(6, 2);
        return `${year}-${month}-${day}`;
    }
    return dateStr;
}

function loadEtablissements() {
    $.getJSON('/api/etablissements', function (data) {
        const select = $('#etablissement-select');
        data.forEach(function (etablissement) {
            select.append(`<option value="${etablissement}">${etablissement}</option>`);
        });
    });
}

function fetchInfractions(etablissement) {
    $.getJSON(`/api/infractions/${etablissement}`, function (data) {
        const resultDiv = $('#result');
        resultDiv.empty();

        if (data.length === 0) {
            resultDiv.append('<p>Aucune infraction trouvée pour cet établissement.</p>');
            return;
        }

        let html = '<table class="table table-striped">';
        html += '<thead><tr><th>Date</th><th>Description</th><th>Montant</th></tr></thead><tbody>';
        data.forEach(function (row) {
            const dateFormatted = formatDate(row[2]);
            html += `<tr><td class="date-column">${dateFormatted}</td><td>${row[3]}</td><td>${row[7]}</td></tr>`;
        });
        html += '</tbody></table>';

        resultDiv.append(html);
    });
}

