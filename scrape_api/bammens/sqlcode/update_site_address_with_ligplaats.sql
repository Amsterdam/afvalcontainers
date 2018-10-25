/**
    UPDATE adressen of sites with ligplaatsen if
    the distance is are more then a 10 meter improvement.
**/

CREATE INDEX if not exists liggeo ON bag_ligplaats USING GIST (geometrie);

update afvalcontainers_site st set
	straatnaam = lig_opr,
	huisnummer = lig_hn,
	distance = lig_distance
from (
select
    s.id,
    straatnaam,
    huisnummer,
    lig._openbare_ruimte_naam as lig_opr,
    lig._huisnummer as lig_hn,
    cast(st_distance(s.geometrie, lig.geometrie) as int) as lig_distance,
    s.distance,
    o.id as code,
    w.address->>'summary' as bammens
from afvalcontainers_site s
left join openbareruimte o on(s.straatnaam = o.display)
cross join lateral (select * from afvalcontainers_well w where s.id = w.site_id limit 1) as w
CROSS JOIN LATERAL
	(select l.geometrie, l."_openbare_ruimte_naam", l."_huisnummer"
     FROM bag_ligplaats l
     ORDER BY
		s.geometrie <-> l.geometrie
     limit 1) as lig
where cast(st_distance(s.geometrie, lig.geometrie) as int) - distance < -10
) as lpselect where lpselect.id = st.id
