/**
    UPDATE adressen of sites with verblijfsobjecten if
    the distance is less then 20 meters and at least
    60 meter improvement of the original.
**/
CREATE INDEX if not exists vbogeo ON bag_verblijfsobject USING GIST (geometrie);


update afvalcontainers_site st set
	straatnaam = vbo_opr,
	huisnummer = vbo_hn,
	distance = vbo_distance
from (
select
    s.id as site_id,
    straatnaam,
    huisnummer,
    v._openbare_ruimte_naam as vbo_opr,
    v._huisnummer as vbo_hn,
    cast(st_distance(s.geometrie, v.geometrie) as int) as vbo_distance,
    s.distance,
    o.id as code,
    w.address->>'summary' as bammens,
    w.id
from afvalcontainers_site s
left join openbareruimte o on(s.straatnaam = o.display)
CROSS JOIN lateral (select * FROM afvalcontainers_well w WHERE s.id = w.site_id limit 1) as w
CROSS JOIN LATERAL
	(select v.geometrie, v."_openbare_ruimte_naam", v."_huisnummer"
     FROM bag_verblijfsobject v
     ORDER BY
		s.geometrie <-> v.geometrie
     limit 1) AS v
WHERE cast(st_distance(s.geometrie, v.geometrie) AS int) - distance < -60
AND cast(st_distance(s.geometrie, v.geometrie) AS int) < 20
) AS s_vbo where s_vbo.site_id = st.id
