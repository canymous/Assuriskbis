--
--Question 1
--
SELECT * FROM fact_sinistre_meteo LIMIT 20;
--Afficher, pour chaque région, les trois sinistres dont le montant estimé est le plus élevé.
--region_sinistre | rang | sinistre_id | type_sinistre | montant_estime

select fsm.region_sinistre  , row_number() over (partition by fsm.montant_estime order by fsm.montant_estime ), fsm.sinistre_id , fsm.type_sinistre , fsm.montant_estime  
from fact_sinistre_meteo fsm 

with sinistre_meteo as (
    select  
        region_sinistre, 
        sinistre_id,
        type_sinistre,
        montant_estime,
        row_number() over (partition by region_sinistre order by montant_estime desc) as rang
    from fact_sinistre_meteo fsm
)
select 
    region_sinistre, 
    sinistre_id, 
    type_sinistre, 
    montant_estime,
    rang
from sinistre_meteo
where rang <= 3;

--
--Question 2
--

--Afficher chaque sinistre avec, à côté, la moyenne des montants de son type, et l’écart entre son montant et cette moyenne.

select 
    sinistre_id,
    type_sinistre,
    montant_estime,
    round(avg(montant_estime) over (partition by type_sinistre)) as moyenne_du_type,
    round(montant_estime - avg(montant_estime) over (partition by type_sinistre)) as ecart
from fact_sinistre_meteo
order by  sinistre_id;

--
--Question 3 : La part de chaque région dans le total
--

with par_region as (
    select  
        region_sinistre,
        count(*) as nb
    from fact_sinistre_meteo
    group by region_sinistre
)
select 
    region_sinistre,
    nb,
    round (nb * 100.0 / sum (nb) over (), 1) as pct
from par_region
order by nb desc;

-- Suite de la QUESTION 3 : Ajout du pourcentage cumulé
WITH par_region AS (
    SELECT 
        region_sinistre,
        COUNT(*) AS nb
    FROM fact_sinistre_meteo
    GROUP BY region_sinistre
),
pourcentages AS (
    SELECT 
        region_sinistre,
        nb,
        ROUND(nb * 100.0 / SUM(nb) OVER (), 1) AS pct
    FROM par_region
)
SELECT 
    region_sinistre,
    nb,
    pct,
    ROUND(SUM(pct) OVER (ORDER BY nb DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 1) AS pct_cumule
FROM pourcentages
ORDER BY nb DESC;

--
-- QUESTION 4 : Le type de sinistre le plus fréquent de chaque ville
--

with compte as (
    select  
        ville_sinistre,
        type_sinistre,
        count (*) as nb
    from fact_sinistre_meteo
    group by ville_sinistre, type_sinistre
),
classement as (
    select  
        ville_sinistre,
        type_sinistre,
        nb,
        row_number() over (
            partition by ville_sinistre 
            order by nb desc
        ) as rang
    from compte
)
select 
    ville_sinistre,
    type_sinistre,
    nb
from classement
where rang = 1
order by nb desc;


