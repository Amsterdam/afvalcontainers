UPDATE kilogram_buurtfractiestatmonth km SET
	containers=bla.containers
FROM (
SELECT b.vollcode buurt_code, count(c) containers, c.waste_name fractie from buurt_simple b, afvalcontainers_well w, afvalcontainers_container c
	 WHERE w.buurt_code = b.vollcode
	 AND c.well_id = w.id
	 GROUP BY (b.vollcode, c.waste_name)
	 ORDER BY containers DESC
) AS bla
WHERE bla.buurt_code = km.buurt_code
AND	(bla.fractie = km.fractie OR
        (km.fractie = 'Kunststof' AND bla.fractie = 'Plastic'));


UPDATE kilogram_buurtfractiestatweek km SET
	containers=bla.containers
FROM (
SELECT b.vollcode buurt_code, count(c) containers, c.waste_name fractie from buurt_simple b, afvalcontainers_well w, afvalcontainers_container c
	 WHERE w.buurt_code = b.vollcode
	 AND c.well_id = w.id
	 GROUP BY (b.vollcode, c.waste_name)
	 ORDER BY containers DESC
) AS bla
WHERE bla.buurt_code = km.buurt_code
AND	(bla.fractie = km.fractie OR
	(km.fractie = 'Kunststof' AND bla.fractie = 'Plastic'));
