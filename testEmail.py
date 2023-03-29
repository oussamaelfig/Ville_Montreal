import yaml

from populate_database import send_new_contrevenants_email

with open("email_config.yaml", 'r') as stream:
    email_config = yaml.safe_load(stream)

sample_new_contrevenants = [
    "Établissement 1",
    "Établissement 2",
    "Établissement 3",
    "Établissement 4"
]

send_new_contrevenants_email(sample_new_contrevenants, email_config)
