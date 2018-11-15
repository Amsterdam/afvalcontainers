/*
    combine sites based on bgt and non bgt if they overlap
*/

/* reset site_id on wells */
UPDATE afvalcontainers_well
SET site_id = null;


update afvalcontainers_site ts set
	geometrie=newgeo,
	active=4
from (
	select a.id aid, b.id, st_union(a.geometrie, b.geometrie) newgeo from afvalcontainers_site a, afvalcontainers_site b
	where a.bgt_based
	and st_overlaps(a.geometrie, b.geometrie)
	and a.id != b.id
) as overlapping
where overlapping.aid = ts.id;


/* delete the old sites */
delete from afvalcontainers_site s
where id = ANY(
	select a.id from afvalcontainers_site b, afvalcontainers_site a
	where st_overlaps(a.geometrie, b.geometrie)
	and a.id != b.id
	and b.bgt_based = true
	and a.bgt_based = false
);
