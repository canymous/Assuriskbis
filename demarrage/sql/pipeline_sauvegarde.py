import os
os.makedirs("sorties", exist_ok=True)
import io
import json
import time
from getpass import getpass
import pandas as pd
import psycopg2

mot_de_passe = getpass("Mot de passe PostgreSQL : ")
connexion = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="ASSURISKBIS",
    user="postgres",
    password=mot_de_passe,
)
connexion.autocommit = True
curseur = connexion.cursor()
print("connexion ouverte")

#01_init.sql
#02_clean.sql
#03_tables_meteo.sql
#04_rattachement.sql
#05_croisement.sql
#06_controles.sql

#La question, et elle n’est pas technique : pourquoi 04_rattachement.sql
# ne peut-il pas tourner avant que la météo soit chargée ? Écrivez votre réponse.

#Parce que rattachement va lier les donnees meteo aux villes.

# 1. Première liste d'étapes SQL (avant la météo)
etapes_avant = [
    ("01_init.sql", "Reinitialiser la base"),
    ("02_clean.sql", "Construire la couche propre"),
    ("03_tables_meteo.sql", "Creer les tables qui attendent la meteo"),
]

journal = []
controles = []

for fichier, libelle in etapes_avant:
  debut = time.time()
  requete = open("sql/" + fichier, encoding="utf-8").read()
  curseur.execute(requete)
  duree = round(time.time() - debut, 1)
  journal.append([fichier, libelle, "SQL", duree])
  print(" [SQL]", libelle, "-", duree, "s")

# Contrôle intermédiaire
verification = pd.read_sql(
    "SELECT count(*) AS n FROM clean_fact_sinistre", connexion
)
print(" controle : clean_fact_sinistre =", verification["n"][0], "lignes")

# 2. Partie Python : Météo (JSON) + Villes (CSV)
debut = time.time()
meteo_brute = json.load(
    open("donnees/meteo_30_villes.json", encoding="utf-8")
)
morceaux = []
for localisation in meteo_brute:
  tableau = pd.DataFrame(localisation["daily"])
  tableau["latitude"] = localisation["latitude"]
  tableau["longitude"] = localisation["longitude"]
  morceaux.append(tableau)
meteo = pd.concat(morceaux, ignore_index=True)

tampon = io.StringIO()
meteo.to_csv(tampon, index=False, header=False)
tampon.seek(0)
curseur.copy_expert(
    "COPY meteo_assurrisk FROM STDIN WITH (FORMAT csv)", tampon
)
duree_meteo = round(time.time() - debut, 1)
journal.append(["meteo_json", "Chargement meteo Python", "Python", duree_meteo])
print(" [PYTHON]", len(meteo), "lignes de meteo chargees")

debut = time.time()
villes_df = pd.read_csv("donnees/villes_coordonnees_meteo.csv")
tampon_villes = io.StringIO()
villes_df.to_csv(tampon_villes, index=False, header=False)
tampon_villes.seek(0)
curseur.copy_expert(
    "COPY villes_coordonnees_meteo FROM STDIN WITH (FORMAT csv)", tampon_villes
)
duree_villes = round(time.time() - debut, 1)
journal.append(["villes_csv", "Chargement villes Python", "Python", duree_villes])
print(" [PYTHON]", len(villes_df), "lignes de villes chargees")

# 3. Deuxième liste d'étapes SQL (après la météo)
etapes_apres = [
    ("04_rattachement.sql", "Rattachement meteo et villes"),
]
etapes_apres.append(("05_croisement.sql", "Croisement sinistres et meteo"))
etapes_apres.append(("06_controles.sql", "Verifier la qualite des donnees"))

for fichier, libelle in etapes_apres:
  debut = time.time()
  requete = open("sql/" + fichier, encoding="utf-8").read()
  curseur.execute(requete)
  duree = round(time.time() - debut, 1)
  journal.append([fichier, libelle, "SQL", duree])
  print(" [SQL]", libelle, "-", duree, "s")

# Sauvegarde du journal global
suivi = pd.DataFrame(
    journal, columns=["fichier", "etape", "outil", "secondes"]
)
suivi.to_csv(
    "sorties/journal_pipeline.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig",
)

# Sauvegarde des contrôles
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

print("Pipeline terminé avec succès !")



