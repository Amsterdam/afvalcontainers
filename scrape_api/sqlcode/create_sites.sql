create index on bag_verblijfsobject(_openbare_ruimte_naam);

SELECT
    Concat(x, '-', y, '-', b.code) as id,
    ST_Transform(
        ST_Centroid(site_geometrie), 4326) as centroid,
    site_geometrie as geometrie,
    s.display as stadsdeel_naam,
    s.code as stadseel,
    opr.display as straatnaam,
    vbo._huisnummer,
    vbo._huisletter,
    b.naam as buurt
FROM bgt_clusters c
left join stadsdeel s on ST_DWithin(c.site_geometrie, s.wkb_geometry, 0)
left join buurt_simple b on ST_DWithin(c.site_geometrie, b.wkb_geometry, 0)
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
