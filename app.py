# ELFO74030209
# OUSSAMA EL-FIGHA
# el-figha.oussama@courrier.uqam.ca

from datetime import datetime
import hashlib
import json
import os
import sqlite3
from xml.etree.ElementTree import Element, SubElement, tostring
from flask import Flask, render_template, request, jsonify, redirect, \
    flash, url_for, Response
from flask_login import LoginManager, login_user, logout_user, \
    login_required, current_user
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
from werkzeug.utils import secure_filename

# Obtenir le chemin du répertoire contenant le fichier app.py
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'mP01FxJ0fV0bwQq0nXdlPx0kVxryWBoK'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

EXTENSIONS_IMAGES = {'jpg', 'png'}

plainte_schema = {
    "type": "object",
    "properties": {
        "nom_etablissement": {"type": "string"},
        "adresse": {"type": "string"},
        "ville": {"type": "string"},
        "date_visite": {"type": "string", "format": "date"},
        "nom_client": {"type": "string"},
        "description_probleme": {"type": "string"}
    },
    "required": ["nom_etablissement", "adresse", "ville", "date_visite",
                 "nom_client", "description_probleme"]
}

user_schema = {
    "type": "object",
    "properties": {
        "nom_complet": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "etablissements_surveilles": {"type": "array",
                                      "items": {"type": "string"}},
        "mot_de_passe": {"type": "string", "minLength": 8}
    },
    "required": ["nom_complet", "email", "mot_de_passe"]
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[
        1].lower() in EXTENSIONS_IMAGES


# Classe pour représenter l'utilisateur
class User:
    def __init__(self, id, nom_complet, email, etablissements_surveilles,
                 mot_de_passe, photo_de_profil=None):
        self.id = id
        self.nom_complet = nom_complet
        self.email = email
        self.etablissements_surveilles = etablissements_surveilles
        self.mot_de_passe = mot_de_passe
        self.photo_de_profil = photo_de_profil

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# Fonction pour charger un utilisateur à partir de la base de données
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    c.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        return User(*user_data)
    else:
        return None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['POST'])
def search():
    etablissement = request.form.get('etablissement')
    proprietaire = request.form.get('proprietaire')
    rue = request.form.get('rue')

    # Valider les donnees du formulaire
    errors = []
    if len(etablissement) > 100:
        errors.append(
            'Le nom d\'établissement ne doit pas dépasser 100 caractères.')
    if len(proprietaire) > 100:
        errors.append(
            'Le nom de propriétaire ne doit pas dépasser 100 caractères.')
    if len(rue) > 100:
        errors.append('Le nom de rue ne doit pas dépasser 100 caractères.')
    if not etablissement and not proprietaire and not rue:
        errors.append('Veuillez saisir au moins un critère de recherche.')
    if errors:
        return render_template('home.html', errors=errors)

    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    query = "SELECT * FROM poursuite WHERE "
    params = []
    if etablissement:
        query += "etablissement LIKE ? AND "
        params.append('%' + etablissement + '%')
    if proprietaire:
        query += "proprietaire LIKE ? AND "
        params.append('%' + proprietaire + '%')
    if rue:
        query += "adresse LIKE ? AND "
        params.append('%' + rue + '%')
    query = query[:-5]  # Remove the last "AND"
    c.execute(query, params)
    results = [
        (
            r[0], r[1], datetime.strptime(r[2], "%Y%m%d").strftime("%Y-%m-%d"),
            r[3], r[4], datetime.strptime(r[5], "%Y%m%d").strftime("%Y-%m-%d"),
            r[6], r[7], r[8], r[9], r[10],
            datetime.strptime(r[11], "%Y%m%d").strftime("%Y-%m-%d"), r[12]
        )
        for r in c.fetchall()
    ]

    conn.close()

    # Afficher les resultats de recherches
    return render_template('results.html', results=results,
                           num_results=len(results))


@app.route('/contrevenants')
def get_contrevenants_between_dates():
    start_date = request.args.get('du')
    end_date = request.args.get('au')

    # Valider le format de la date
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'error': 'Format de date invalide. Utilisez le format ISO 8601 : '
                     'YYYY-MM-DD'}), 400

    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    query = """SELECT etablissement, COUNT(*) as nb_contraventions
        FROM poursuite WHERE date >= ? AND date <= ?
        GROUP BY etablissement"""
    params = [start_date, end_date]
    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    # Retourner le resultat sous format JSON
    contrevenants = []
    for row in results:
        contrev = {
            'etablissement': row[0],
            'nb_contraventions': row[1]
        }
        contrevenants.append(contrev)
    return Response(json.dumps(contrevenants, indent=4, ensure_ascii=False),
                    mimetype='application/json')


@app.route('/infractions_par_etablissement_json')
def get_infractions():
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    query = """
        SELECT etablissement, COUNT(*) AS nb_infractions
        FROM poursuite
        GROUP BY etablissement
        ORDER BY nb_infractions DESC
    """
    c.execute(query)
    results = c.fetchall()
    conn.close()

    # Transformer les donnees en format JSON
    infractions = []
    for row in results:
        infraction = {
            'etablissement': row[0],
            'nb_infractions': row[1]
        }
        infractions.append(infraction)

    return Response(json.dumps(infractions, indent=4, ensure_ascii=False),
                    mimetype='application/json')


@app.route('/infractions_par_etablissement_xml')
def get_infractions_by_establishment_xml():
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()

    query = '''
        SELECT etablissement, COUNT(*) AS nb_infractions 
        FROM poursuite
        GROUP BY etablissement
        ORDER BY nb_infractions DESC
    '''
    c.execute(query)
    results = c.fetchall()
    conn.close()

    # Build la reponse XML
    root = Element('etablissements')
    for row in results:
        etablissement = SubElement(root, 'etablissement',
                                   nb_infractions=str(row[1]))
        etablissement.text = row[0]

    return app.response_class(
        response=tostring(root),
        status=200,
        mimetype='application/xml')


@app.route('/infractions_par_etablissement_csv')
def get_etablissements_infractions_csv():
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    query = '''
        SELECT etablissement, COUNT(*) as nb_infractions
        FROM poursuite
        GROUP BY etablissement
        ORDER BY nb_infractions DESC
    '''
    c.execute(query)
    results = c.fetchall()
    conn.close()

    # generer le fichier CSV
    output = "Etablissement,Nombre d'infractions\n"
    for row in results:
        output += f"{row[0]},{row[1]}\n"

    # Retourner la reponse CSV
    response = Response(output, mimetype='text/csv')
    response.headers[
        "Content-Disposition"] = "attachment; filename=etablissements" \
                                 "-infractions.csv"
    return response


@app.route('/contrevenants-liste')
def contrevenants_liste():
    return render_template('contrevenants.html')


@app.route('/api/etablissements')
def api_etablissements():
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT etablissement FROM poursuite ORDER BY etablissement")
    results = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in results])


@app.route('/api/infractions/<etablissement>')
def api_infractions(etablissement):
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    c.execute("SELECT * FROM poursuite WHERE etablissement = ?",
              (etablissement,))
    results = c.fetchall()
    conn.close()
    return jsonify(results)


@app.route('/api/utilisateurs', methods=['POST'])
def creer_utilisateur():
    try:
        # Valider le JSON reçu
        validate(instance=request.json, schema=user_schema)

        # Hasher le mot de passe
        mot_de_passe_hashe = hashlib.sha256(
            request.json['mot_de_passe'].encode('utf-8')).hexdigest()

        # Insérer l'utilisateur dans la base de données
        conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
        c = conn.cursor()
        c.execute("""
            INSERT INTO utilisateurs (nom_complet, email, etablissements_surveilles, mot_de_passe)
            VALUES (?, ?, ?, ?)
        """, (request.json['nom_complet'], request.json['email'],
              json.dumps(request.json.get('etablissements_surveilles', [])),
              mot_de_passe_hashe))
        conn.commit()
        conn.close()

        # Retourner un message de succès
        return jsonify({"message": "Utilisateur créé avec succès"}), 201

    except ValidationError as e:
        return jsonify({"erreur": str(e)}), 400
    except SchemaError as e:
        return jsonify({"erreur": str(e)}), 400
    except sqlite3.IntegrityError as e:
        return jsonify({"erreur": "L'adresse e-mail est déjà utilisée"}), 400
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


@app.route('/create-user-profile')
def create_user_profile():
    return render_template('create_user_profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
        c = conn.cursor()
        c.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
        user_data = c.fetchone()
        conn.close()

        if user_data and hashlib.sha256(
                password.encode('utf-8')).hexdigest() == user_data[4]:
            user = User(*user_data)
            login_user(user)
            return redirect(url_for('edit_etablissements'))
        else:
            return render_template('login.html',
                                   error="Adresse e-mail ou mot de passe "
                                         "incorrect.")

    return render_template('login.html')


@app.route('/edit_etablissements', methods=['GET', 'POST'])
def edit_etablissements():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        etablissements = request.form.get('etablissements')

        conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
        c = conn.cursor()
        c.execute(
            "UPDATE utilisateurs SET etablissements_surveilles = ? WHERE id "
            "= ?",
            (etablissements, current_user.id))
        conn.commit()
        conn.close()

        flash("La liste des établissements surveillés a été mise à jour.",
              "success")
        return redirect(url_for('edit_etablissements'))

    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
    c = conn.cursor()
    c.execute(
        "SELECT etablissements_surveilles FROM utilisateurs WHERE id = ?",
        (current_user.id,))
    etablissements = c.fetchone()[0]
    conn.close()

    return render_template('edit_etablissements.html',
                           etablissements=etablissements)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('Aucun fichier n\'a été sélectionné', 'danger')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('Aucun fichier n\'a été sélectionné', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            secure_filename(file.filename)
            file_content = file.read()
            conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
            c = conn.cursor()
            c.execute(
                "UPDATE utilisateurs SET photo_de_profil = ? WHERE id = ?",
                (file_content, current_user.id))
            conn.commit()
            conn.close()
            flash('Photo de profil téléversée avec succès', 'success')
            return redirect(url_for('upload_photo'))
        else:
            flash('Format de fichier non autorisé', 'danger')
            return redirect(request.url)
    return render_template('upload_photo.html')


@app.route('/api/plaintes', methods=['POST'])
def ajouter_plainte():
    try:
        validate(instance=request.json, schema=plainte_schema)

        conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
        c = conn.cursor()
        c.execute("""
            INSERT INTO plaintes (nom_etablissement, adresse, ville, date_visite, nom_client, description_probleme)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (request.json['nom_etablissement'], request.json['adresse'],
              request.json['ville'], request.json['date_visite'],
              request.json['nom_client'],
              request.json['description_probleme']))
        conn.commit()
        conn.close()

        return jsonify({"message": "Plainte ajoutée avec succès"}), 201

    except ValidationError as e:
        return jsonify({"erreur": str(e)}), 400
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


@app.route('/depot-plainte')
def depot_plainte():
    return render_template('plainte.html')


@app.route('/doc')
def api_doc():
    return render_template('doc.html')


if __name__ == '__main__':
    app.run(debug=True)
