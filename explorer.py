import pandas as pd
import psycopg2
import warnings
from getpass import getpass

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
mot_de_passe = getpass("Mot de passe PostgreSQL : ")
import psycopg2
connexion = psycopg2.connect(
    "dbname=ASSURISKBIS user=postgres password=POSTgres123!* host=localhost port=5432 client_encoding=utf8"
)
df = pd.read_sql("SELECT * FROM fact_sinistre_meteo", connexion)
df["montant_estime"] = df["montant_estime"].astype(float)
df["franchise"] = df["franchise"].astype(float)
df["date_survenance"] = pd.to_datetime(df["date_survenance"])
df["date_declaration"] = pd.to_datetime(df["date_declaration"])

# Nombre total de lignes
print(df.shape)

# Valeurs manquantes
print(df.isna().sum())

# Montant le plus faible, le plus élevé
print("Min : {df['montant_estime'].min()}")
print("Max : {df['montant_estime'].max()}")

# Types de sinistres differents
print("Type de sinistre")
print(df['type_sinistre'].value_counts())

# Moyenne et médiane
print("Moyenne : {df['franchise'].mean()}")
print("Médiane : {df['franchise'].median()}")

## 1. CE QUI M'ÉTONNE │
# l'observation, avec son chiffre │
# Les 30 villes françaises de la table affichent toutes le « dégât des eaux » comme premier type de sinistre en volume

## 2. CE QUE JE PROPOSE │
# mon explication, en UNE phrase │
# C'est simplement le reflet de la répartition nationale globale où le dégât des eaux est largement majoritaire partout

## 3. CE QUE JE DEVRAIS VOIR SI C'EST VRAI │
# Si mon explication est vraie, je devrais voir la part du dégât des eaux rester stable et proche de la moyenne nationale 
# dans chaque ville, plutôt que d'être ultra-dominante partout par hasard.
# Si mon hypothèse était fausse, je devrais observer

# À ÉCRIRE AVANT DE TAPER LA MOINDRE COMMANDE │
# et : si c'était faux, je verrais quoi ? │
# Si elle est fausse, je verrais certaines villes où un autre sinistre dépasse largement, ou des proportions totalement 
# disparates d'une ville à l'autre

## 4. CE QUE JE VOIS VRAIMENT │
# les chiffres obtenus │

print (df["type_sinistre"].value_counts(normalize=True))
# type_sinistre
# Dégât des eaux           
# 0.291453
# Vol                      
# 0.174822

## 5. MA CONCLUSION, ET MA CONFIANCE │
# confirmée / infirmée / je ne sais pas

# Conclusion : Hypothèse confirmée.S
# Sur quoi elle s'appuie : La vérification ville par ville montre que la part du dégât des eaux reste stable 
# et homogène sur l'ensemble du territoire (avec un minimum de 23,1 % et un maximum de 34,8 % pour une moyenne globale de 29,1 %). 
# Sa présence en tête dans toutes les villes n'est donc pas une anomalie locale ou un hasard, mais le reflet direct de sa domination 
# structurelle au niveau national.   
# Degré de confiance : Élevé, car la tendance est validée de manière uniforme sur l'ensemble des 30 villes de la table

lille = df[df["ville_sinistre"] == "Lille"]
print(lille["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

# Dégât des eaux           28.4
# Tempête                  14.8
# Vol                      14.8
# Bris de glace            13.6
# Grêle                    13.6
# Responsabilité civile     8.6
# Incendie                  6.1

lyon = df[df["ville_sinistre"] == "Lyon"]
print(lyon["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

marseille = df[df["ville_sinistre"] == "Marseille"]
print(marseille["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

bordeaux = df[df["ville_sinistre"] == "Bordeaux"]
print(bordeaux["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

nantes = df[df["ville_sinistre"] == "Nantes"]
print(nantes["type_sinistre"].value_counts(normalize=True).mul(100).round(1))

part = (df.groupby("ville_sinistre")["type_sinistre"]
.apply(lambda s: s.value_counts(normalize=True).mul(100).round(1)))
print(part.xs("Dégât des eaux", level=1).describe())

# count    30.000000
# mean     29.263333
# std       2.705994
# min      23.100000
# 25%      27.775000
# 50%      29.300000
# 75%      31.100000
# max      34.800000
# Name: type_sinistre, dtype: float64

# Mercredi 18 novembre
# Exercice 1

# « Si c'était vraiment une catastrophe climatique, alors je devrais voir une explosion d'un type de sinistre paticulier dans les données. »

# « Si ce n'en était pas une, je verrais plutôt se dessiner la tendance habituelle »

# « Si c'était vraiment une catastrophe climatique, alors je devrais voir une trace dans les colonnes qui indiquent le temps (comme weather code). »

# « Si ce n'en était pas une, je verrais plutôt ... »

# « Si c'était vraiment une catastrophe climatique, alors je devrais voir un pic de sinistres du même type plutôt qu'une hausse constante tout au long du mois »

# « Si ce n'en était pas une, je verrais plutôt ... »


octobre = df[(df["date_survenance"] >= "2025-10-01") &
(df["date_survenance"] <= "2025-10-31")]

reste = df[~df.index.isin(octobre.index)]

par_jour = octobre.groupby(octobre["date_survenance"].dt.day).size()
print(par_jour.describe())

print(len(octobre), len(reste))
# 1940 10158

print(df["date_survenance"].min(), df["date_survenance"].max())
# 2024-01-01 00:00:00 2025-10-28 00:00:00

# Calcul de la répartition géographique en pourcentage (%) pour octobre
occ_reg = octobre["region_sinistre"].value_counts(normalize=True).mul(100).round(1)

# Calcul de la répartition géographique en pourcentage (%) pour le reste
reste_reg = reste["region_sinistre"].value_counts(normalize=True).mul(100).round(1)

# Regroupement dans un même tableau pour comparer côte à côte
comparaison_regions = pd.DataFrame({
    "Octobre (%)": occ_reg,
    "Reste (%)": reste_reg
})

print(comparaison_regions)

# Conclusion : Hypothèse de la catastrophe climatique infirmée.

# Sur quoi elle s'appuie : L'analyse de la répartition géographique montre que la hausse d'octobre est répartie 
# de façon homogène sur l'ensemble du territoire (les parts par région en octobre sont quasi identiques à celles 
# du reste de l'année). Une tempête ou une catastrophe naturelle locale aurait provoqué une surreprésentation 
# massive sur une ou deux régions ciblées, ce qui n'est pas le cas ici.

# Degré de confiance : Élevé, car la vérification géographique contredit formellement l'hypothèse d'un événement localisé.

# Exercice 2










