create index on bag_verblijfsobject(_openbare_ruimte_naam);

INSERT INTO afvalcontainers_site
SELECT DISTINCT
    Concat(x, '-', y, '-', s.code, b.code) as id,
    b.code as buurtcode,
    s.code as stadseel,
    s.display as stadsdeel_naam,
    opr.display as straatnaam,
    cast(vbo._huisnummer as integer) as huisnummer,
    true as bgt_based,
    ST_Transform(centroid, 4326) as centroid,
    site_geometrie as geometrie
FROM bgt_clusters c
left join stadsdeel s on ST_DWithin(c.centroid, s.wkb_geometry, 0)
left join buurt_simple b on ST_DWithin(c.centroid, b.wkb_geometry, 0)
cross join lateral
	(select
		o.display,
		o.wkb_geometry,
		o.id
	from openbareruimte o
	order by
		o.wkb_geometry <-> c.site_geometrie
	limit 1) as opr
CROSS JOIN LATERAL
	(SELECT
		v._huisnummer, v._huisletter, v._huisnummer_toevoeging
     FROM bag_verblijfsobject v
     where opr.display = v."_openbare_ruimte_naam"
     ORDER BY
	c.site_geometrie <-> v.geometrie
     limit 1) as vbo;
