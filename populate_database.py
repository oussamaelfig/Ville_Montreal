import csv
import requests
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()


def send_new_contrevenants_email(new_contrevenants, email_config):
    email_content = "Liste des nouveaux contrevenants:\n\n"

    for contrevenant in new_contrevenants:
        email_content += f"- {contrevenant}\n"

    msg = MIMEText(email_content)
    msg["Subject"] = "Nouveaux contrevenants"
    msg["From"] = email_config["from_email"]
    msg["To"] = email_config["to_email"]

    try:
        with smtplib.SMTP_SSL(email_config["smtp_server"],
                              email_config["smtp_port"]) as server:
            server.login(email_config["from_email"],
                         email_config["email_password"])
            server.send_message(msg)
            print(
                f"Email sent to {email_config['to_email']} at {datetime.now()}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def update_database():
    # Load email configuration from YAML file
    with open("email_config.yaml", 'r') as stream:
        email_config = yaml.safe_load(stream)

    # Download the data from the URL
    url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
    response = requests.get(url)

    # Parse the CSV data
    poursuites = csv.DictReader(response.content.decode('utf-8').splitlines())

    # Connect to the database
    conn = sqlite3.connect('db/db')
    c = conn.cursor()

    # Retrieve all existing ids
    c.execute("SELECT id_poursuite FROM poursuite")
    existing_ids = set(row[0] for row in c.fetchall())

    # Track new contrevenants
    new_contrevenants = set()

    # Insert the new data into the table
    for poursuite in poursuites:
        id_poursuite = int(poursuite['id_poursuite'])
        if id_poursuite not in existing_ids:
            business_id = poursuite['business_id']
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

            # Insert new record
            c.execute(
                "INSERT INTO poursuite (id_poursuite, buisness_id, date, "
                "description, adresse, date_jugement, etablissement, "
                "montant, proprietaire, ville, statut, date_statut,"
                " categorie) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (id_poursuite, business_id, date, description, adresse,
                 date_jugement, etablissement, montant, proprietaire,
                 ville, statut, date_statut, categorie))

            # Add the new contrevenant to the set
            new_contrevenants.add(etablissement)

            # Update existing_ids
            existing_ids.add(id_poursuite)

    # Commit changes to the database
    conn.commit()

    # Close the database connection
    conn.close()

    # If there are new contrevenants, send an email
    if new_contrevenants:
        send_new_contrevenants_email(new_contrevenants, email_config)


# Schedule the update_database function to run every day
scheduler.add_job(update_database, 'interval', days=1)

# Run the update_database function immediately
update_database()
