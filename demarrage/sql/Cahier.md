# 1. Troisième fonction (ajouter_au_journal) : 
nommée ainsi car c'est un verbe d'action qui dit exactement qu'elle ajoute une ligne au journal en centralisant l'unique journal.append.   
# 2. Erreur / piège : 
calculer la durée à l'intérieur de la fonction au lieu de la mesurer juste après l'étape (sans erreur bloquante, mais avec de fausses durées) ou oublier "statut" dans columns (ValueError sur le nombre de colonnes).  
# À revoir demain matin : 
vérifier que 01_init.sql dépasse bien 20 secondes dans sorties/journal_pipeline.csv et m'assurer de bien maîtriser quand passer debut en paramètre. 

Sans git add préalable, Git n'inclut pas la modification dans le commit et signale qu'aucun changement n'a été ajouté à l'index pour être validé.

Après git restore, le fichier reste cassé et échoue au lancement parce que la commande restaure l'état du dernier commit enregistré — qui contenait déjà la version cassée —, ce qui montre qu'il faut toujours vérifier son code avant de commiter.

# À noter dans votre cahier avant de partir
**Une chose que vous savez faire aujourd’hui et que vous ne saviez pas faire lundi matin.**
**Ce qui reste flou — la chose que vous reprendriez en premier.**
**Le moment de la semaine où vous avez compris quelque chose : lequel, et quoi.**

Une chose que je sais faire aujourd'hui et que je ne savais pas faire lundi matin : `mettre un projet Python/SQL sous Git`(git init, .gitignore, git diff, git commit, git restore) en retirant d'abord les mots de passe en clair avec getpass pour ne pas les graver dans l'historique.

`Ce qui reste flou` — la chose que je reprendrais en premier : la restauration vers un commit antérieur lorsqu'une version cassée a déjà été commitée (git revert ou restauration depuis un commit précis), ainsi que la vérification fine des résultats de corrélations et d'octobre 2025 dans explorer.py.

`Le moment de la semaine où j'ai compris quelque chose`: pendant l'enquête et la factorisation du pipeline, j'ai compris l'intérêt de poser ses critères de vérification avant d'explorer les chiffres et de centraliser les écritures de journal (ajouter_au_journal) dans une seule fonction afin d'éviter de biaiser l'analyse ou d'oublier un point de mise à jour.

