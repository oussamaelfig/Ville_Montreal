document.getElementById('submit-plainte').addEventListener('click', function () {
    const formData = {
        nom_etablissement: document.getElementById('nom_etablissement').value,
        adresse: document.getElementById('adresse').value,
        ville: document.getElementById('ville').value,
        date_visite: document.getElementById('date_visite').value,
        nom_client: document.getElementById('nom_client').value,
        description_probleme: document.getElementById('description_probleme').value,
    };

    fetch('/api/plaintes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else {
                alert('Erreur: ' + data.erreur);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert("Une erreur s'est produite lors de l'envoi de la plainte.");
        });
});