/*
	First lookup available volumne and containers for measurements
*/

UPDATE kilogram_sitefractiestatweek k set
	volume=f.volume_m3,
	containers=f.containers
from afvalcontainers_sitefractie f, afvalcontainers_site s
WHERE
	k.site_id = s.short_id
AND	s.id = f.site_id
AND	(f.fractie = k.fractie or
	 (k.fractie = 'Kunststof' and f.fractie = 'Plastic'));


UPDATE kilogram_sitefractiestatmonth k set
	volume=f.volume_m3,
	containers=f.containers
from afvalcontainers_sitefractie f, afvalcontainers_site s
WHERE
	k.site_id = s.short_id
AND	s.id = f.site_id
AND	(f.fractie = k.fractie or
	 (k.fractie = 'Kunststof' and f.fractie = 'Plastic'));



