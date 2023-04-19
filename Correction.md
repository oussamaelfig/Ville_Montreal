### A1

**Script de téléchargement et d'insertion des données**: Pour tester cette fonctionnalite, aller sur le fichier **populate_database.py**, la methode updatre_database, importe les donnees de l url https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv

#### A2

**Application Flask avec recherche de contraventions**: pour tester cette fonctionnalite aller sur le site, home page et vous trouverez le formulaire pour chercher les contraventions, vous remplisser le formulaire et vous cliquez sur **Rechercher**, vous serez redirige vers une nouvelle page avec les resultats de recherche

#### A3

**BackgroundScheduler pour la mise à jour des données**: vous trouverez le code dans le fichier **populate_database.py** à la ligne 142

#### A4

**API REST pour obtenir la liste des contraventions entre deux dates**: allez sur la bare de lien et ajouter vers la fin de l URL  */contrevenants?du=2020-05-08&au=2022-05-15* vous pouvez modifier les dates a partir de ce lien

#### A5

**Recherche rapide de contraventions entre deux dates**: allez dans le home page en bas vous trouverez un formulaire pour saisir deux dates, après un tableau réactif va être affiche juste en bas pour le résultat de la recherche

#### A6

**Recherche par nom de restaurant**: allez dans la barre de navigation, vous trouverez l'onglet **service**, cliquez dessus et cliquez en bas sur **Recherche d'infractions**, vous pouvez ensuite choisir un restaurant parmi ceux dans la liste déroulante 

#### B1

**Envoi de nouvelles contraventions par courriel**: vous trouverez le code pour cette fonctionnalité dans le fichier **populate_database.py**, la méthode send_new_contrevenants_email envoie un courriel au cas ou on trouve un nouveau contrevenant

#### B2

**Publication automatique sur Reddit**: allez sur le fichier popualte_database.py, vous trouverez le code pour cette fonctionnalite dans la methode **post_to_reddit**

#### C1

**API REST pour obtenir la liste des établissements ayant commis des
infractions en JSON**: pour tester ajouter  */infractions_par_etablissement_json* a la fin du l URL.
exemple : http://127.0.0.1:5000/infractions_par_etablissement_json

#### C2

**Service pour obtenir les données au format XML**: pour tester, ajoutez */infractions_par_etablissement_xml* a la fin du l URL.
exemple : http://127.0.0.1:5000/infractions_par_etablissement_xml

#### C3

**Service pour obtenir les données au format CSV**: pour tester, ajoutez */infractions_par_etablissement_csv* a la fin du l URL.
exemple : http://127.0.0.1:5000/infractions_par_etablissement_csv

#### D1

**Service REST pour faire une demande d'inspection à la ville**: Pour tester cette fonctionnalité, aller sur la barre de navigation, cliquer sur services, cliquez par la suite sur **déposer une plainte**, vous trouverez après le formulaire pour déposer une plainte

#### E1

**Service REST pour créer un profil d'utilisateur**: Pour tester cette fonctionnalité, aller sur la barre de navigation, cliquer sur services, cliquez par la suite sur **Creer un profil utilisateur**, vous trouverez la page pour creer un nouvel utilisateur

#### E2

**Page web d'authentification et de gestion du profil**: Aller sur la barre de navigation, cliquer sur **Se connecter**, après la connexion vous allez être redirige a la page **Modifier etablissements** pour modifier la liste des établissements a surveiller. Vous pouvez aussi téléverser une photo de profil en allant dans la page **Téléverser une photo de profil**. A la fin vous pouvez vous deconecter en cliquant sur **Se déconnecter**.

#### F1

**Déploiement sur PythonAnyWhere**: Voici le site de deployement http://elfidev.pythonanywhere.com/


