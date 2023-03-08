CREATE TABLE poursuite
(
    id_poursuite  INTEGER PRIMARY KEY,
    buisness_id   INTEGER,
    date          TEXT,
    description   TEXT,
    adresse       VARCHAR(200),
    date_jugement TEXT,
    etablissement viarchar(100),
    montant       INTEGER,
    proprietaire  varchar(100),
    ville         varchar(50),
    statut        varchar(50),
    date_statut   TEXT,
    categorie     varchar(100)

);