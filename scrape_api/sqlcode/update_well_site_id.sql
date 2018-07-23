UPDATE afvalcontainers_well well
SET site_id = lala.id
FROM (
	SELECT s.id, w.id AS wid FROM afvalcontainers_site s
	LEFT JOIN afvalcontainers_well w ON ST_Within(w.geometrie_rd, s.geometrie)
) lala
WHERE well.id = lala.wid
