/* create index on bag_verblijfsobject(_openbare_ruimte_naam); */

INSERT INTO afvalcontainers_site (
	id,
	buurt_code,
	stadsdeel,
	stadsdeel_naam,
	straatnaam,
	huisnummer,
	bgt_based,
	centroid,
	geometrie,
	distance
)
SELECT
    Concat(x, '-', y, '-', s.code, b.code) as id,
    b.code as buurt_code,
    s.code as stadseel,
    s.display as stadsdeel_naam,
    opr.display as straatnaam,
    cast(vbo._huisnummer as integer) as huisnummer,
    false as bgt_based,
    ST_Transform(centroid, 4326) as centroid,
    site_geometrie as geometrie,
    cast(ST_Distance(centroid, vbo.geometrie) as int) as distance
FROM well_nobgt_clusters c
left join stadsdeel s on ST_DWithin(c.centroid, s.wkb_geometry, 0)
left join buurt_simple b on ST_DWithin(c.centroid, b.wkb_geometry, 0)
cross join lateral
	(select
		o.display,
		o.wkb_geometry,
		o.id
	from openbareruimte o, bag_verblijfsobject v
	where o.opr_type = 'Weg'
	and v."_openbare_ruimte_naam" = o.display
	order by
		o.wkb_geometry <-> c.site_geometrie
	limit 1) as opr
CROSS JOIN LATERAL
	(SELECT
		v._huisnummer, v._huisletter,
		v._huisnummer_toevoeging, v.geometrie
     FROM bag_verblijfsobject v
     where opr.display = v."_openbare_ruimte_naam"
     ORDER BY
	c.site_geometrie <-> v.geometrie
     limit 1) as vbo;
