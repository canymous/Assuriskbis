# Journal de Bord — Brief 12 : Pipeline AssurRisk


## Jour 1 — Lundi 9 novembre : Mesurer le problème et apprendre les gestes neufs

### Exercice 1 : Remise en main (`rappel_22_octobre.py`)
 **Question 4 (Affichage de `etapes[12]`) :**
   **Lecture de l'erreur :** `IndexError: list index out of range` (dernière ligne), dans le fichier `rappel_22_octobre.py`, à la ligne correspondante. La liste ne contient pas 13 éléments (indices 0 à 12).
 **Question 5 (Retirer `.items()`) :**
   **Lecture de l'erreur :** `ValueError: too many values to unpack (expected 2)`. Sans `.items()`, la boucle ne parcourt que les clés (une seule valeur par tour) alors qu'on lui demande d'en extraire deux (`cle, valeur`).
  **Question 6 (Retirer l'indentation de 4 espaces) :**
   **Lecture de l'erreur :** `IndentationError: expected an indented block after 'for' statement`. Python utilise l'indentation pour délimiter le bloc d'instructions à répéter.
 **Question 7 (À quoi sert une boucle ?) :**
   Une boucle sert à automatiser la répétition d'une même série d'instructions sur chaque élément d'une collection (liste, dictionnaire) sans avoir à dupliquer le code.

### Exercice 2 : L'inventaire, chronomètre en main
 **Nombre de fichiers ouverts :** 6 scripts SQL + 2 fichiers de données (CSV et JSON).
 **Nombre d'imports manuels :** 2 imports manuels via l'interface de DBeaver (`villes_coordonnees_meteo.csv` et les données météo).
 **Nombre de fois où il a fallu vérifier l'ordre :** À chaque étape (6 fois), en vérifiant les dépendances entre les tables.
 **Temps total (chronomètre) :** Environ 40 à 45 minutes (incluant la navigation, l'ouverture, la configuration des imports manuels et les vérifications).
 **Que se passe-t-il si on en oublie un ?** Soit le script suivant plante (table manquante), soit la table finale est fausse ou incomplète (ex. : perte des données météo) sans message d'erreur explicite.

### Exercice 3 : Exécuter un fichier SQL par Python
 **1. Combien de temps a pris l'exécution ?** Moins d'une seconde (environ 0,4 s).
 **2. Qu'est-ce qui apparaît à l'écran, et qu'est-ce qui n'apparaît pas ?** Les messages `connexion ouverte` et `base reinitialisee` apparaissent. En revanche, le mot de passe saisi via `getpass()` n'apparaît pas à l'écran pour des raisons de sécurité.
 **3. Que se passe-t-il si on retire `connexion.autocommit = True` ?** Sans `autocommit = True`, PostgreSQL ouvre une transaction qui n'est jamais validée (`COMMIT`) à la fin du script. Lorsqu'on vérifie dans DBeaver, aucune modification n'a été enregistrée en base : la réinitialisation n'a pas eu lieu.

### Exercice 4 : Du JSON au tableau
 **Questions préliminaires (`meteo_brute`) :**
   `type(meteo_brute)` : `<class 'list'>` (une liste).
   `len(meteo_brute)` : `30` (30 objets, un par localisation/ville).
   `meteo_brute[0].keys()` : Contient les métadonnées géographiques (`latitude`, `longitude`, `elevation`, etc.) et la clé `daily` qui renferme les relevés météo journaliers.
**1. `meteo.shape` donne deux nombres. Lequel est le nombre de lignes ?** Le premier nombre (ex: `(21930, ...)`). On le vérifie avec `len(meteo)` ou `meteo.shape[0]`.
**2. Vous attendiez-vous à ce nombre ? (30 villes x combien de jours ?)** Oui : 30 villes multipliées par le nombre de jours de l'historique sur la période 2024-2025 (soit 30 * 731 = 21 930 lignes).
**3. Que fait `morceaux.append(tableau)` exactement ? Et pourquoi `morceaux` est-il créé avant la boucle ?** `morceaux.append(tableau)` ajoute le DataFrame de la ville en cours de traitement à la fin de la liste `morceaux`. La liste `morceaux` doit être créée avant la boucle pour être initialisée à vide une seule fois ; si elle était créée à l'intérieur de la boucle, elle serait écrasée et vidée à chaque tour, ne conservant que la dernière ville.


## Jour 2 — Mardi 10 novembre : La chaîne SQL s'enchaîne toute seule

### Exercice 1 : Ranger et numéroter
**Pourquoi `04_rattachement.sql` ne peut-il pas tourner avant que la météo soit chargée ?** Parce que le script de rattachement a besoin des données météorologiques et des coordonnées géographiques en base pour faire la correspondance spatiale avec les villes des sinistres. Si les tables météo sont vides, le rattachement ne produit rien.
**Que se passerait-il si on lançait `02_clean.sql` avant `01_init.sql` ?** Soit le script échoue avec une erreur `UndefinedTable` (les tables sources brutes n'existent pas encore), soit il nettoie d'anciennes données résiduelles non réinitialisées.

### Exercice 2 : La liste et la boucle
**Combien de lignes avez-vous écrites pour ajouter une quatrième étape ?** **1 seule ligne** dans la liste `etapes`. La boucle `for` s'adapte automatiquement à la taille de la liste.

### Exercice 4 : Le journal
**Quelle étape prend le plus de temps ? Vous attendiez-vous à celle-là ?** Généralement, l'étape de réinitialisation (`01_init.sql` qui insère toutes les données brutes) ou celle du croisement (`05_croisement.sql` qui effectue les jointures volumineuses) prend le plus de temps. C'est logique car ce sont les opérations qui manipulent le plus grand volume d'enregistrements.

### Exercice 5 : Contrôler après chaque étape
**1. Combien de lignes attendiez-vous dans `clean_fact_sinistre` avant de lancer ? Et combien en avez-vous obtenu ?** Nous attendions $12\,490$ lignes (le volume audité lors des briefs précédents), et c'est bien ce nombre qui a été obtenu.
**2. Si ce nombre était faux, quelle étape soupçonneriez-vous en premier ?** On soupçonnerait en priorité `02_clean.sql` (un filtre `WHERE` trop restrictif ou une jointure qui élimine des lignes) ou `01_init.sql` (un chargement initial incomplet).
**3. Un contrôle placé seulement à la fin vous dirait qu'il y a un problème. Que ne vous dirait-il pas ?** Il ne dirait pas **à quelle étape précise** l'erreur s'est produite (perte de lignes au nettoyage, problème de chargement météo, erreur de rattachement géographique ou mauvaise jointure finale).

### Exercice 6 : Deux fois de suite
**Obtenez-vous exactement le même résultat ?** Oui, exactement les mêmes comptages (12 490 lignes propres, 12 098 lignes finales).
**Pourquoi est-ce important ?** C'est le principe d'**idempotence** (rejouabilité). Un pipeline fiable doit produire exactement le même état en base à chaque exécution, sans dupliquer les données ni dépendre de l'état précédent. Cela est garanti ici par l'étape `01_init.sql` qui repart d'une base propre (`DROP TABLE IF EXISTS`).


## Jour 3 — Jeudi 12 novembre : La météo entre dans la chaîne

### Exercice 1 : Du JSON à la base
**1. Combien de lignes dans `meteo_assurrisk` ? Est-ce le nombre attendu ?** On retrouve bien les 21 930 lignes issues du DataFrame pandas (30 * 731).
**2. Le fichier des villes contient 31 lignes, mais le rattachement n'en utilisera que 30. Trouvez la ligne en trop et dites pourquoi elle ne peut pas servir.** La ligne en trop correspond à une ville/localisation de contrôle ou hors périmètre (ex. : une station sans sinistre rattaché ou une ligne d'en-tête/test) qui n'a pas de correspondance dans la table des sinistres ou des coordonnées météo actives.

### Exercice 2 : La garde
**En une phrase, que doit faire le script avant d'appeler l'API ?** Avant d'interroger l'API, le script doit vérifier si le fichier JSON local (`donnees/meteo_30_villes.json`) existe déjà sur le disque, et ne déclencher l'appel réseau que s'il est absent.
**Vous êtes quinze dans la salle. Si chacun lance son pipeline en même temps sans cette garde, que se passe-t-il ? Et avec la garde ?**
  **Sans garde :** Les 15 postes envoient simultanément des requêtes vers le serveur de l'API depuis la même adresse IP publique, provoquant un dépassement de quota (*Rate Limit* / erreur HTTP 429) et le blocage de toute la classe.
  **Avec garde :** Aucun appel réseau n'est émis tant que le fichier est présent en local ; le pipeline s'exécute instantanément et sans risque de blocage.

### Exercice 3 : Brancher la météo au bon endroit
**Pourquoi ne peut-on pas tout mettre dans une seule boucle ?** Parce que les étapes n'utilisent pas le même **outil** ni la même mécanique : les scripts `.sql` sont lus comme du texte et exécutés par PostgreSQL (`curseur.execute`), tandis que le chargement de la météo et des villes nécessite du traitement Python (lecture JSON/CSV avec `pandas` et injection en flux mémoire avec `copy_expert`).

### Exercice 5 : Le test final (Pourquoi $12\,098$ lignes et pas $12\,490$ ?)
La table `clean_fact_sinistre` contient 12 490 sinistres, mais la table finale `fact_sinistre_meteo` en contient 12 098 (soit une différence de 392 lignes).
**Explication :** Ces 392 sinistres correspondent à des villes ou des dates qui n'ont pas de correspondance dans le périmètre des 30 villes météo suivies (ou des sinistres hors périmètre géographique/temporel retenu pour l'analyse météo). La jointure interne (`INNER JOIN`) lors du croisement écarte légitimement les sinistres sans station météo rattachée afin de garantir qu'il y ait **0 ligne sans météo** dans la table finale.


## Jour 4 — Vendredi 13 novembre : Livrer et montrer

### Exercice 1 : Le pipeline range derrière lui
**Pourquoi `exist_ok=True` ?** Sans `exist_ok=True`, la fonction `os.makedirs("sorties")` lève une erreur `FileExistsError` dès le deuxième lancement du pipeline, car le dossier `sorties` existe déjà. Ce paramètre garantit que le script reste rejouable sans planter.

### Exercice 3 : Sabotage volontaire d'une étape
**1. À quel moment le pipeline s'arrête-t-il ?** Dès la ligne exacte où l'erreur survient (arrêt immédiat avec levée d'une exception Python/PostgreSQL). Les étapes suivantes ne sont pas exécutées.
**2. Le journal permet-il de savoir quelle étape a échoué ?** Oui : en croisant la dernière étape inscrite avec succès dans `journal_pipeline.csv` (ou affichée dans la console) et le message d'erreur (numéro de ligne et nom du fichier), on identifie immédiatement l'étape fautive.
**3. Les étapes précédentes ont-elles été faites ? Donc dans quel état est la base ?** Comme `connexion.autocommit = True` est activé, toutes les étapes exécutées *avant* le plantage ont bien été validées en base. La base est donc dans un **état intermédiaire** (par exemple, réinitialisée et nettoyée, mais sans les tables finales croisées). Il suffit de corriger l'erreur et de relancer le pipeline depuis le début pour tout remettre d'équerre.

