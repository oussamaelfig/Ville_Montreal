import csv
import requests
import sqlite3
from datetime import datetime
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import praw
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os

basedir = os.path.abspath(os.path.dirname(__file__))

scheduler = BackgroundScheduler()
scheduler.start()


def send_new_contrevenants_email(new_contrevenants, email_config):
    email_content = "Liste des nouveaux contrevenants:\n\n"

    for contrevenant in new_contrevenants:
        email_content += f"- {contrevenant}\n"

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = email_config['sendinblue_api_key']

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration))

    send_email = sib_api_v3_sdk.SendSmtpEmail(
        subject="Nouveaux contrevenants",
        html_content=email_content,
        sender={"name": "Votre nom", "email": email_config["from_email"]},
        to=[{"email": email_config["to_email"]}]
    )

    try:
        api_response = api_instance.send_transac_email(send_email)
        print(
            f"Email sent to {email_config['to_email']} at {datetime.now()}, "
            f"Message ID: {api_response.message_id}")
    except ApiException as e:
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
    conn = sqlite3.connect(os.path.join(basedir, 'db/db'))
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
        post_to_reddit(new_contrevenants)
        send_new_contrevenants_email(new_contrevenants, email_config)


def post_to_reddit(new_contrevenants):
    # Reddit's credentials and settings
    reddit = praw.Reddit(
        client_id="MkTFCzX5gCNmGsfbdSc4JQ",
        client_secret="haBic3DYNDxVGIl23eydW7udm5e66g",
        user_agent="inspectionmtl/0.1 (by u/elfiDev)",
        username="elfiDev",
        password="Admin@2023",
    )

    # Create the post content
    post_title = "Nouveaux contrevenants"
    post_content = "Liste des nouveaux contrevenants :\n\n"
    for contrevenant in new_contrevenants:
        post_content += f"- {contrevenant}\n"

    # Publish the post on a specific subreddit link :
    # https://old.reddit.com/r/inspectionMTL/comments/122744c
    # /rinspectionmtl_lounge/?ref=share&ref_source=link
    subreddit = reddit.subreddit("r/inspectionMTL")
    subreddit.submit(post_title, selftext=post_content)


# Schedule the update_database function to run every day
scheduler.add_job(update_database, 'interval', days=1)

# Run the update_database function immediately
update_database()
