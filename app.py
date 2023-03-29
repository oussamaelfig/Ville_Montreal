import json
import datetime
from flask import Flask, render_template, request, jsonify, Response, redirect, \
    flash, url_for
from xml.etree.ElementTree import Element, SubElement, tostring
import hashlib
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
from flask_login import LoginManager, login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename
import psycopg2

app = Flask(__name__)
app.secret_key = 'mP01FxJ0fV0bwQq0nXdlPx0kVxryWBoK'

# Ajoutez ces lignes après la création de l'objet app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = {'jpg', 'png'}


def create_connection():
    try:
        conn = psycopg2.connect(
            dbname="db",
            user="postgres",
            password="Admin@2023",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[
        1].lower() in ALLOWED_EXTENSIONS


# Créez une classe pour représenter l'utilisateur
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


# Ajoutez cette fonction pour charger un utilisateur à partir de la base de
# données
@login_manager.user_loader
def load_user(user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
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
    # Retrieve form data
    etablissement = request.form.get('etablissement')
    proprietaire = request.form.get('proprietaire')
    rue = request.form.get('rue')

    # Validate form data
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

    # Retrieve data from database
    conn = create_connection()
    c = conn.cursor()
    query = "SELECT * FROM poursuite WHERE "
    params = []
    if etablissement:
        query += "etablissement LIKE %s AND "
        params.append('%' + etablissement + '%')
    if proprietaire:
        query += "proprietaire LIKE %s AND "
        params.append('%' + proprietaire + '%')
    if rue:
        query += "adresse LIKE %s AND "
        params.append('%' + rue + '%')
    query = query[:-5]  # Remove the last "AND"
    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    # Display search results
    return render_template('results.html', results=results,
                           num_results=len(results))


@app.route('/contrevenants')
def get_contrevenants_between_dates():
    # Retrieve query parameters
    start_date = request.args.get('du')
    end_date = request.args.get('au')

    # Validate date format
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'error': 'Format de date invalide. Utilisez le format ISO 8601 : '
                     'YYYY-MM-DD'}), 400

    # Retrieve data from database
    conn = create_connection()
    c = conn.cursor()
    query = """SELECT etablissement, COUNT(*) as nb_contraventions
        FROM poursuite WHERE (date >= %s AND date <= %s)
        GROUP BY etablissement"""
    params = [start_date, end_date]
    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    # Return results in JSON format
    contrevenants = []
    for row in results:
        contrev = {
            'etablissement': row[0],
            'nb_contraventions': row[1]
        }
        contrevenants.append(contrev)
    return Response(json.dumps(contrevenants, indent=4, ensure_ascii=False),
                    mimetype='application/json')


@app.route('/doc-api')
def api_doc():
    with open('doc.raml', 'r') as f:
        raml = f.read()
    return render_template('api_doc.html', raml=raml)


@app.route('/infractions_par_etablissement_json')
def get_infractions():
    # Retrieve data from database
    conn = create_connection()
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

    # Transform data into JSON format
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
    conn = create_connection()
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

    # Build XML response
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
    # Retrieve data from database
    conn = create_connection()
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

    # Generate CSV file
    output = "Etablissement,Nombre d'infractions\n"
    for row in results:
        output += f"{row[0]},{row[1]}\n"

    # Return CSV response
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
    conn = create_connection()
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT etablissement FROM poursuite ORDER BY etablissement")
    results = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in results])


@app.route('/api/infractions/<etablissement>')
def api_infractions(etablissement):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM poursuite WHERE etablissement = %s",
              (etablissement,))
    results = c.fetchall()
    conn.close()
    return jsonify(results)


@app.route('/api/utilisateurs', methods=['POST'])
def creer_utilisateur():
    # JSON Schema pour valider le document JSON reçu
    schema = {
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

    try:
        # Valider le JSON reçu
        validate(instance=request.json, schema=schema)

        # Hasher le mot de passe
        mot_de_passe_hashe = hashlib.sha256(
            request.json['mot_de_passe'].encode('utf-8')).hexdigest()

        # Insérer l'utilisateur dans la base de données
        conn = create_connection()
        c = conn.cursor()

        # Vérifier si l'email existe déjà dans la base de données
        c.execute("SELECT * FROM utilisateurs WHERE email = %s",
                  (request.json['email'],))
        existing_user = c.fetchone()
        print(f"Utilisateur existant : {existing_user}")

        if existing_user is not None:
            return jsonify(
                {"erreur": "L'adresse e-mail est déjà utilisée"}), 400

        # Si l'email n'existe pas, insérer l'utilisateur
        c.execute("""
            INSERT INTO utilisateurs (nom_complet, email, etablissements_surveilles, mot_de_passe)
            VALUES (%s, %s, %s, %s)
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
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if 'email' in str(e):
            return jsonify(
                {"erreur": "L'adresse e-mail est déjà utilisée"}), 400
        else:
            return jsonify({"erreur": f"Erreur d'intégrité : {str(e)}"}), 400
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

        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
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

        conn = create_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE utilisateurs SET etablissements_surveilles = %s WHERE id "
            "= %s",
            (etablissements, current_user.id))
        conn.commit()
        conn.close()

        flash("La liste des établissements surveillés a été mise à jour.",
              "success")
        return redirect(url_for('edit_etablissements'))

    conn = create_connection()
    c = conn.cursor()
    c.execute(
        "SELECT etablissements_surveilles FROM utilisateurs WHERE id = %s",
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
            filename = secure_filename(file.filename)
            file_content = file.read()
            conn = create_connection()
            c = conn.cursor()
            c.execute(
                "UPDATE utilisateurs SET photo_de_profil = %s WHERE id = %s",
                (file_content, current_user.id))
            conn.commit()
            conn.close()
            flash('Photo de profil téléversée avec succès', 'success')
            return redirect(url_for('upload_photo'))
        else:
            flash('Format de fichier non autorisé', 'danger')
            return redirect(request.url)
    return render_template('upload_photo.html')


if __name__ == '__main__':
    app.run(debug=True)
