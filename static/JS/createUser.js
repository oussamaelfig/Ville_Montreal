        $('#create-user-form').submit(function (event) {
            event.preventDefault();

            const username = $('#username').val();
            const email = $('#email').val();
            const password = $('#password').val();
            const confirmPassword = $('#confirm_password').val();
            const etablissementsSurveilles = $('#etablissements-surveilles').val().split(',').map(e => e.trim());

            if (password !== confirmPassword) {
                alert("Les mots de passe ne correspondent pas.");
                return;
            }

            const userData = {
                "nom_complet": username,
                "email": email,
                "mot_de_passe": password,
                "etablissements_surveilles": etablissementsSurveilles
            };

            $.ajax({
                type: "POST",
                url: "/api/utilisateurs",
                contentType: "application/json",
                data: JSON.stringify(userData),
                dataType: "json",
                success: function (response) {
                    alert("Utilisateur créé avec succès !");
                    window.location.href = '/';
                },
                error: function (response) {
                    alert("Erreur lors de la création de l'utilisateur : " + response.responseJSON.erreur);// a corriger
                }
            });
        });