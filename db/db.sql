CREATE TABLE poursuite
(
    id_poursuite  INTEGER PRIMARY KEY,
    buisness_id   INTEGER,
    date          TEXT,
    description   TEXT,
    adresse       VARCHAR(200),
    date_jugement TEXT,
    etablissement VARCHAR(100),
    montant       INTEGER,
    proprietaire  VARCHAR(100),
    ville         VARCHAR(50),
    statut        VARCHAR(50),
    date_statut   TEXT,
    categorie     VARCHAR(100)
);


CREATE TABLE utilisateurs
(
    id                        INTEGER PRIMARY KEY,
    nom_complet               TEXT        NOT NULL,
    email                     TEXT UNIQUE NOT NULL,
    etablissements_surveilles TEXT,
    mot_de_passe              TEXT        NOT NULL,
    photo_de_profil           BLOB
);

CREATE TABLE plaintes
(
    id                   INTEGER PRIMARY KEY,
    nom_etablissement    TEXT NOT NULL,
    adresse              TEXT NOT NULL,
    ville                TEXT NOT NULL,
    date_visite          DATE NOT NULL,
    nom_client           TEXT NOT NULL,
    description_probleme TEXT NOT NULL
);

