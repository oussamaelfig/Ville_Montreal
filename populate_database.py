import csv
import requests
import sqlite3

# Download the data from the URL
url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0' \
      '/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
response = requests.get(url)

# Parse the CSV data
poursuites = csv.DictReader(response.text.splitlines())

# Connect to the database
conn = sqlite3.connect('db/db')
c = conn.cursor()

# Insert the data into the database
for poursuite in poursuites:
    id_poursuite = poursuite['id_poursuite']
    buisness_id = poursuite['business_id']
    date = poursuite['date']
    description = poursuite['description']
    adresse = poursuite['adresse']
    date_jugement = poursuite['date_jugement']
    etablissement = poursuite['etablissement']
    montant = poursuite['montant']
    proprietaire = poursuite['proprietaire']
    ville = poursuite['ville']
    statut = poursuite['statut']
    date_statut = poursuite['date_statut']
    categorie = poursuite['categorie']
    c.execute("INSERT INTO poursuite (id_poursuite, buisness_id, date, "
              "description, adresse, date_jugement, etablissement, montant, "
              "proprietaire, ville, statut, date_statut, categorie) VALUES ("
              "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id_poursuite,
                                                         buisness_id, date,
                                                         description,
                                                         adresse,
                                                         date_jugement,
                                                         etablissement,
                                                         montant,
                                                         proprietaire,
                                                         ville, statut,
                                                         date_statut,
                                                         categorie))

# Commit the changes and close the connection
conn.commit()
conn.close()
