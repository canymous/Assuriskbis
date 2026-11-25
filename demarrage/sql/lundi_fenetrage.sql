--
-- =====================================================================
-- QUESTION 1 : Les trois sinistres les plus chers de chaque région
-- Colonnes : region_sinistre | rang | sinistre_id | type_sinistre | montant_estime
-- Vérification : 36 lignes (12 régions x 3)
-- =====================================================================
WITH sinistre_meteo AS (
    SELECT
        region_sinistre,
        ROW_NUMBER() OVER (
            PARTITION BY region_sinistre
            ORDER BY montant_estime DESC
        ) AS rang,
        sinistre_id,
        type_sinistre,
        montant_estime
    FROM fact_sinistre_meteo
)
SELECT
    region_sinistre,
    rang,
    sinistre_id,
    type_sinistre,
    montant_estime
FROM sinistre_meteo
WHERE rang <= 3
ORDER BY region_sinistre, rang;


-- =====================================================================
-- QUESTION 2 : L'écart entre un sinistre et la moyenne de son type
-- Colonnes : sinistre_id | type_sinistre | montant_estime | moyenne_du_type | ecart
-- Vérification : 12 098 lignes ; 1re ligne = 1 | Dégât des eaux | 2070.00 | 4478 | -2408
-- =====================================================================
SELECT
    sinistre_id,
    type_sinistre,
    montant_estime,
    ROUND(AVG(montant_estime) OVER (PARTITION BY type_sinistre)) AS moyenne_du_type,
    ROUND(montant_estime - AVG(montant_estime) OVER (PARTITION BY type_sinistre)) AS ecart
FROM fact_sinistre_meteo
ORDER BY sinistre_id;


-- =====================================================================
-- QUESTION 3 : La part de chaque région dans le total (+ bonus cumulé)
-- Colonnes : region_sinistre | nb | pct (| pct_cumule)
-- Vérification : 12 lignes ; somme manuelle de pct = 99,9 ; pct_cumule final = 100,0
-- =====================================================================
WITH par_region AS (
    SELECT
        region_sinistre,
        COUNT(*) AS nb
    FROM fact_sinistre_meteo
    GROUP BY region_sinistre
)
SELECT
    region_sinistre,
    nb,
    ROUND(nb * 100.0 / SUM(nb) OVER (), 1) AS pct,
    ROUND(SUM(nb) OVER (ORDER BY nb DESC) * 100.0 / SUM(nb) OVER (), 1) AS pct_cumule
FROM par_region
ORDER BY nb DESC;


-- =====================================================================
-- QUESTION 4 : Le type de sinistre le plus fréquent de chaque ville
-- Colonnes : ville_sinistre | type_sinistre | nb
-- Vérification : 30 lignes (1 par ville)
-- =====================================================================
WITH compte AS (
    SELECT
        ville_sinistre,
        type_sinistre,
        COUNT(*) AS nb
    FROM fact_sinistre_meteo
    GROUP BY ville_sinistre, type_sinistre
),
classement AS (
    SELECT
        ville_sinistre,
        type_sinistre,
        nb,
        ROW_NUMBER() OVER (
            PARTITION BY ville_sinistre
            ORDER BY nb DESC
        ) AS rang
    FROM compte
)
SELECT
    ville_sinistre,
    type_sinistre,
    nb
FROM classement
WHERE rang = 1
ORDER BY nb DESC;


