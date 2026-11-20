# =====================================================================
#  AssurRisk — pipeline.py
#  Etat a la fin du JEUDI 12 novembre
#
#  Chaque bloc porte le numero de l'exercice qui l'a produit.
# =====================================================================

import psycopg2
from getpass import getpass
import time
import pandas as pd
import json
import io
import os
import warnings

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

#=======================================================
# Vendredi exercice 1
# exist_ok=True c'est meme chose en sql DROP TABLE IF EXISTS
#=======================================================

os.makedirs("sorties", exist_ok=True)

# ---------------------------------------------------------------------
#  LA CONNEXION           (lundi — demonstration 1)
# ---------------------------------------------------------------------
mot_de_passe = getpass("Mot de passe PostgreSQL : ")

connexion = psycopg2.connect(host="localhost", port=5432, dbname="ASSURISKBIS",
                             user="postgres", password=mot_de_passe)
connexion.autocommit = True
curseur = connexion.cursor()
print("connexion ouverte")
journal = []
def jouer_sql(fichier, libelle):
    #for fichier, libelle in etapes_avant:
    debut = time.time()
    requete = open("sql/" + fichier, encoding="utf-8").read()
    curseur.execute(requete)
    duree = round(time.time() - debut, 1)
    journal.append([fichier, libelle, "SQL", duree])
    pd.DataFrame(journal, columns=["fichier", "etape", "outil", "secondes"]).to_csv(
    "sorties/journal_pipeline.csv", sep=";", decimal=",",
    index=False, encoding="utf-8-sig")
    print("  [SQL]", libelle, "-", duree, "s")




# =====================================================================
#  EXERCICE 3 — on coupe la boucle en deux : PREMIERE MOITIE
#
#  Ces trois etapes doivent tourner AVANT que la meteo arrive.
#  03 cree les deux tables vides qui vont l'accueillir.
# =====================================================================
etapes_avant = [
    ("01_init.sql",         "Reinitialiser la base"),
    ("02_clean.sql",        "Construire la couche propre"),
    ("03_tables_meteo.sql", "Creer les tables qui attendent la meteo"),
]

for fichier, libelle in etapes_avant:
    jouer_sql(fichier, libelle)


# =====================================================================
#  L'ETAPE PYTHON — ce que SQL ne sait pas faire
# =====================================================================
debut = time.time()

# ---- EXERCICE 2 — la garde -------------------------------------------
#  On regarde si le fichier est deja la AVANT de penser a l'API.
#  Un pipeline qui redemande ce qu'il a deja n'est pas plus
#  automatique : il est juste plus impoli.
fichier_json = "donnees/meteo_30_villes.json"
print("  fichier meteo deja present :", os.path.exists(fichier_json))

# ---- EXERCICE 1 — du JSON au tableau ---------------------------------
#  Le JSON est une LISTE de 30 dictionnaires (lundi, demonstration 2).
#  On fait un petit tableau de chacun, et on les empile.
meteo_brute = json.load(open(fichier_json, encoding="utf-8"))

morceaux = []
for localisation in meteo_brute:
    tableau = pd.DataFrame(localisation["daily"])
    tableau["latitude"]  = localisation["latitude"]
    tableau["longitude"] = localisation["longitude"]
    morceaux.append(tableau)

meteo = pd.concat(morceaux, ignore_index=True)

# ---- EXERCICE 1 — du tableau a la base -------------------------------
#  Le tampon est un fichier qui n'existe que dans la memoire.
#  seek(0) = rembobiner avant de relire. Sans lui : 0 ligne, sans erreur.
tampon = io.StringIO()
meteo.to_csv(tampon, index=False, header=False)
tampon.seek(0)
curseur.copy_expert("COPY meteo_assurrisk FROM STDIN WITH (FORMAT csv)", tampon)

#  Le referentiel des villes est DEJA un CSV : pas besoin de pandas,
#  il part directement dans la base. HEADER true saute la ligne de titres.
curseur.copy_expert(
    "COPY villes_coordonnees_meteo FROM STDIN WITH (FORMAT csv, HEADER true)",
    open("donnees/villes_coordonnees_meteo.csv", encoding="utf-8"))

duree = round(time.time() - debut, 1)
journal.append(["pipeline.py", "Charger la meteo et les villes", "PYTHON", duree])
pd.DataFrame(journal, columns=["fichier", "etape", "outil", "secondes"]).to_csv(
"sorties/journal_pipeline.csv", sep=";", decimal=",",
index=False, encoding="utf-8-sig")
print("  [PYTHON]", len(meteo), "lignes de meteo chargees -", duree, "s")


# =====================================================================
#  EXERCICE 3 — DEUXIEME MOITIE  +  EXERCICE 4
#
#  Ces deux etapes LISENT la meteo : elles ne peuvent pas tourner
#  avant le bloc ci-dessus. C'est tout l'interet de la coupure.
# =====================================================================
etapes_apres = [
    ("04_rattachement.sql", "Rattacher les points meteo aux villes"),
    ("05_croisement.sql",   "Croiser les sinistres avec la meteo"),
]

    

for fichier, libelle in etapes_apres:
    jouer_sql(fichier, libelle)

# ---------------------------------------------------------------------
#  LE JOURNAL            (mardi — exercice 4)
#  La colonne "outil" montre l'alternance : SQL SQL SQL PYTHON SQL SQL
# ---------------------------------------------------------------------
suivi = pd.DataFrame(journal, columns=["fichier", "etape", "outil", "secondes"])
suivi.to_csv("sorties/journal_pipeline.csv", sep=";", decimal=",",
             index=False, encoding="utf-8-sig")


# =====================================================================
#  EXERCICE 5 — LE TEST
#  Les six nombres qui disent si la semaine est reussie.
# =====================================================================
controles = pd.read_sql("""
    SELECT (SELECT count(*) FROM clean_fact_sinistre)                           AS sinistres_propres,
           (SELECT count(*) FROM meteo_assurrisk)                               AS lignes_meteo,
           (SELECT count(DISTINCT ville) FROM meteo_assurrisk_ville)            AS villes_meteo,
           (SELECT count(*) FROM fact_sinistre_meteo)                           AS lignes_finales,
           (SELECT count(*) FROM fact_sinistre_meteo WHERE weather_code IS NULL) AS sans_meteo,
           (SELECT count(*) FROM (SELECT ville, time FROM meteo_assurrisk_ville
                                  GROUP BY 1,2 HAVING count(*) > 1) z)          AS meteo_en_double
""", connexion)

print()
print("CONTROLES")
for colonne in controles.columns:
    print("   ", colonne, ":", controles[colonne][0])

controles.to_csv("sorties/controles.csv", sep=";", decimal=",",
                 index=False, encoding="utf-8-sig")

curseur.close()
connexion.close()
