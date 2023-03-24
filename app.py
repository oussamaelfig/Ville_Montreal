import json
import csv
import logging
import uuid
import datetime
from flask import Flask, render_template, request, jsonify, Response
from xml.etree.ElementTree import Element, SubElement, tostring
import sqlite3
import hashlib
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


# def format_date(date_string):
#     date_obj = datetime.strptime(date_string, "%Y%m%d")
#     return date_obj.strftime("%Y-%m-%d")


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
    conn = sqlite3.connect('db/db')
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
    conn = sqlite3.connect('db/db')
    c = conn.cursor()
    query = """SELECT etablissement, COUNT(*) as nb_contraventions
        FROM poursuite WHERE date >= ? AND date <= ?
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


@app.route('/doc')
def doc():
    with open('doc.raml', 'r') as f:
        raml = f.read()
    return render_template('doc.html', raml=raml)


@app.route('/infractions')
def get_infractions():
    # Retrieve data from database
    conn = sqlite3.connect('db/db')
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
    conn = sqlite3.connect('db/db')
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


@app.route('/etablissements-infractions.csv')
def get_etablissements_infractions_csv():
    # Retrieve data from database
    conn = sqlite3.connect('db/db')
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
    conn = sqlite3.connect('db/db')
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT etablissement FROM poursuite ORDER BY etablissement")
    results = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in results])


@app.route('/api/infractions/<etablissement>')
def api_infractions(etablissement):
    conn = sqlite3.connect('db/db')
    c = conn.cursor()
    c.execute("SELECT * FROM poursuite WHERE etablissement = ?",
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
        conn = sqlite3.connect('db/db')
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


if __name__ == '__main__':
    app.run(debug=True)
