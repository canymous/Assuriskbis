## Synthèse du Pipeline AssurRisk

### 1. Réinitialiser la base (`01_init.sql`)
**Ce qu'elle fait :** Supprime et recrée l'ensemble des tables du schéma public (assurés, agences, contrats, sinistres, indemnisations) en injectant le jeu de données déterministe 2024-2025 ainsi que les anomalies pédagogiques maîtrisées.
**Ce qu'elle produit :** Les tables brutes initiales peuplées.
**Ce qu'elle contrôle :** L'intégrité de la structure initiale et l'absence de valeurs aberrantes globales.
**Ce qui se passe si elle échoue :** Erreur de connexion ou contrainte de clé étrangère violée ; la base reste dans un état incomplet.

### 2. Construire la couche propre (`02_clean.sql`)
**Ce qu'elle fait :** Nettoie les données brutes, applique la minimisation des PII (suppression nom/prénom/email), calcule les tranches d'âge, filtre les doublons et les anomalies (dates inversées, montants invalides).
**Ce qu'elle produit :** Les 7 tables physiques `clean_*` (ex. `clean_fact_sinistre`).
**Ce qu'elle contrôle :** Le volume de lignes exclues par type d'anomalie et l'unicité des clés primaires.
**Ce qui se passe si elle échoue :** Les tables propres ne sont pas créées, bloquant les étapes aval de rattachement.

### 3. Créer les tables météo (`03_tables_meteo.sql`)
**Ce qu'elle fait :** Crée les tables vides `meteo_assurrisk` et `villes_coordonnees_meteo` destinées à recevoir les données externes.
**Ce qu'elle produit :** Des structures de tables prêtes pour le chargement massif (`COPY`).
**Ce qu'elle contrôle :** L'absence préalable des tables et la conformité des types de données (notamment `NUMERIC(12,7)` pour les coordonnées).
**Ce qui se passe si elle échoue :** Erreur de syntaxe DDL ; les données Python ne pourront pas être insérées.

### 4. Chargement Météo & Villes (Python / Garde API)
**Ce qu'elle fait :** Vérifie la présence du fichier JSON local (garde anti-requête), transforme le JSON Open-Meteo en DataFrame aplati, puis injecte la météo et les coordonnées des villes dans PostgreSQL via `COPY STDIN`.
**Ce qu'elle produit :** Les tables `meteo_assurrisk` et `villes_coordonnees_meteo` alimentées.
**Ce qu'elle contrôle :** Le nombre de lignes chargées en mémoire et la validité du format tabulaire.
**Ce qui se passe si elle échoue :** Absence du fichier source ou erreur d'encodage ; interruption immédiate du script Python avant les requêtes SQL de croisement.

### 5. Rattachement météo aux villes (`04_rattachement.sql`)
**Ce qu'elle fait :** Associe chaque couple de coordonnées météo à la ville de référence la plus proche via un produit cartésien et un calcul de distance euclidienne filtré par `ROW_NUMBER()`.
**Ce qu'elle produit :** La table intermédiaire `meteo_assurrisk_ville` (21 930 lignes attendues).
**Ce qu'elle contrôle :** Le volume exact de lignes et l'unicité des associations ville/date.
**Ce qui se passe si elle échoue :** Jointure vide ou erreur de calcul géométrique ; le croisement suivant ne trouvera aucune correspondance.

### 6. Croisement sinistres x météo (`05_croisement.sql`)
**Ce qu'elle fait :** Joint les sinistres propres (`clean_fact_sinistre`) aux données météorologiques rattachées sur la base de la ville et de la date de survenance.
**Ce qu'elle produit :** La table finale `fact_sinistre_meteo`.
**Ce qu'elle contrôle :** L'absence de doublons et la couverture météo complète.
**Ce qui se passe si elle échoue :** Table finale absente ou incomplète.

### 7. Contrôles finaux (`06_controles.sql`)
**Ce qu'elle fait :** Vérifie l'intégrité finale de la table `fact_sinistre_meteo`.
**Ce qu'elle produit :** Une ligne de synthèse validant les indicateurs clés.
**Ce qu'elle contrôle :** Exactement 12 098 lignes, 0 sinistre sans météo, et 0 doublon sur le couple `(ville, date)`.
**Ce qui se passe si elle échoue :** Le nombre de lignes diverge, signalant un problème en amont dans le nettoyage ou les jointures.