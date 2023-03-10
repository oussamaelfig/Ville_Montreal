import datetime
import json
import csv
from flask import Flask, render_template, request, jsonify, Response
from xml.etree.ElementTree import Element, SubElement, tostring
import sqlite3

app = Flask(__name__)


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
    query = "SELECT * FROM poursuite WHERE date >= ? AND date <= ?"
    params = [start_date, end_date]
    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    # Return results in JSON format
    contrevenants = []
    for row in results:
        contrev = {
            'id_poursuite': row[0],
            'buisness_id': row[1],
            'date': row[2],
            'description': row[3],
            'adresse': row[4],
            'date_jugement': row[5],
            'etablissement': row[6],
            'montant': row[7],
            'proprietaire': row[8],
            'ville': row[9],
            'statut': row[10],
            'date_statut': row[11],
            'categorie': row[12]
        }
        contrevenants.append(contrev)
    return Response(json.dumps(contrevenants, indent=4, ensure_ascii=False),
                    mimetype='application/json')


@app.route('/doc')
def doc():
    with open('api.raml', 'r') as f:
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


if __name__ == '__main__':
    app.run(debug=True)
