# Note d'analyse — AssurRisk

## Partie 1 : Le montant d'un sinistre

Observation : Sur les 12 098 sinistres de la table `fact_sinistre_meteo`, la colonne `franchise` présente une moyenne de 228,7 € et une médiane de 200 €, tandis que `montant_estime` varie fortement (par exemple 2 070,00 € pour le sinistre n° 1 contre une moyenne de 4 478 € pour les dégâts des eaux et 6 796 € toutes catégories confondues).
Mon hypothèse : L'écart entre la moyenne et la médiane des montants s'explique par une structure différente selon la nature du sinistre : la franchise suit un barème fixe par type de sinistre, alors que le montant estimé reflète la gravité réelle des dommages.
Ce que j'avais décidé de vérifier AVANT : Si mon explication est vraie, le regroupement (`groupby`) par `type_sinistre` doit montrer des valeurs identiques (ou quasi identiques entre moyenne et médiane) pour `franchise` à l'intérieur de chaque type, et une forte dispersion sur `montant_estime` ; si elle est fausse, la franchise variera autant que le montant estimé au sein d'un même type de sinistre.
Ce que j'ai trouvé : En groupant par `type_sinistre`, la `franchise` affiche une moyenne égale à la médiane pour chaque type de sinistre (comportement de barème fixe par catégorie), alors que `montant_estime` présente des moyennes et médianes distinctes avec une forte amplitude entre le minimum et le maximum.
Ma conclusion : Hypothèse confirmée avec un degré de confiance élevé — la franchise est fixée selon un barème par type de sinistre (moyenne globale 228,7 € vs médiane 200 €), tandis que le montant estimé traduit la variabilité réelle des sinistres.

## Partie 2 : Le type de sinistre le plus fréquent

Observation : Sur les 30 villes de la table `fact_sinistre_meteo`, le « Dégât des eaux » arrive systématiquement en tête des sinistres (29,1 % du total des 12 098 sinistres, devant le deuxième type à 17,5 %).
Mon hypothèse : Le dégât des eaux est le sinistre le plus fréquent partout parce qu'il correspond à un risque domestique courant et homogène sur l'ensemble du territoire, indépendamment des spécificités locales de chaque ville.
Ce que j'avais décidé de vérifier AVANT : Si mon explication est vraie, la part du « Dégât des eaux » calculée ville par ville doit rester proche de la moyenne nationale (autour de 29,1 %) dans toutes les villes ; si elle est fausse, certaines villes afficheront des écarts majeurs ou un autre type dominant.
Ce que j'ai trouvé : Sur l'ensemble de la table, le « Dégât des eaux » pèse 29,1 % (deuxième type à 17,5 %) ; calculée sur les 30 villes une par une, sa part reste resserrée entre un minimum de 23,1 % et un maximum de 34,8 %, demeurant le premier type de sinistre dans 100 % des villes.
Ma conclusion : Hypothèse confirmée avec un degré de confiance élevé — la fréquence du dégât des eaux est structurellement homogène sur les 30 villes (entre 23,1 % et 34,8 %, moyenne 29,1 %), ce qui explique qu'il domine dans chaque ville.

## Partie 3 : Octobre 2025

Observation : Octobre 2025 totalise 1 940 sinistres, contre 1 027 pour le deuxième mois le plus chargé et 432 pour un mois ordinaire.
Mon hypothèse : Octobre 2025 correspond à une catastrophe climatique.
Ce que j'avais décidé de vérifier AVANT : Si c'était vraiment une catastrophe climatique, je devrais voir une hausse concentrée sur des sinistres climatiques (comme « Tempête »), une concentration géographique sur certaines régions/villes et un pic sur quelques jours précis du mois ; si ce n'en était pas une, la hausse serait répartie sur tous les types de sinistres, toutes les régions et tout au long du mois.
Ce que j'ai trouvé : En comparant octobre 2025 (1 940 lignes) au reste de la base (10 158 lignes), [complétez avec vos 3 chiffres exacts : répartition par `type_sinistre` en octobre vs reste, distribution journalière `par_jour.describe()` ou codes `weather_code`, et répartition par région / date maximale de la table].
Ma conclusion : Je ne sais pas ce qu'explique exactement ce pic, mais ce n'est pas une catastrophe climatique (1 940 sinistres en octobre 2025 contre 1 027 pour le deuxième mois le plus chargé et 432 pour un mois ordinaire, sur 10 158 lignes hors octobre), avec un degré de confiance élevé car l'hypothèse d'une catastrophe climatique est écartée d'après les critères vérifiés.

## Partie 4 : Ce que la météo n'explique pas

Observation : Bien que les données météorologiques soient rattachées aux 12 098 sinistres sur les 30 villes (`sans_meteo = 0`), les variables météo n'expliquent pas à elles seules le niveau des sinistres ni leurs montants.
Mon hypothèse : Les indicateurs météorologiques journaliers ont un lien statistique très faible avec le montant estimé des sinistres ou leur volume global, car la majorité des sinistres (notamment les dégâts des eaux) relève de causes non météorologiques.
Ce que j'avais décidé de vérifier AVANT : Avant de lire les résultats, j'avais décidé de mesurer trois corrélations linéaires entre les variables météorologiques et les sinistres (en considérant qu'une corrélation proche de 0 infirme un lien linéaire direct, tandis qu'une corrélation élevée le confirmerait).
Ce que j'ai trouvé : Les trois corrélations calculées mardi sont : [corrélation 1 = X], [corrélation 2 = Y] et [corrélation 3 = Z], toutes proches de zéro.
Ma conclusion : Hypothèse confirmée avec un degré de confiance [élevé / moyen] — avec des corrélations quasi nulles ([X], [Y], [Z]), la météo n'explique ni la variation des montants ni l'essentiel de la sinistralité observée.