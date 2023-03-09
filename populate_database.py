from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import csv
import requests
import sqlite3

scheduler = BackgroundScheduler()
scheduler.start()


@scheduler.scheduled_job('cron', day_of_week='*', hour=0, minute=0)
def update_database():
    # Download the data from the URL
    url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9' \
          '-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6' \
          '/download/violations.csv'
    response = requests.get(url)

    # Parse the CSV data
    poursuites = csv.DictReader(response.content.decode('utf-8').splitlines())

    # Connect to the database
    conn = sqlite3.connect('db/db')
    c = conn.cursor()

    # Delete all existing data from the table
    c.execute("DELETE FROM poursuite")

    # Insert the new data into the table
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
                  "description, adresse, date_jugement, etablissement, "
                  "montant, proprietaire, ville, statut, date_statut,"
                  " categorie) VALUES ("
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
    print(f"Database updated at {datetime.now()}")
