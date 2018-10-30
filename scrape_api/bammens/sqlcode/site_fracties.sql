truncate table afvalcontainers_sitefractie;

insert into afvalcontainers_sitefractie (
	site_id,
	fractie,
	containers,
	volume_m3
)
select s.id, c.waste_name, count(c), sum(t.volume) from afvalcontainers_site s, afvalcontainers_container c, afvalcontainers_well w, afvalcontainers_containertype t
where w.site_id = s.id
and c.well_id = w.id
and t.id = c.container_type_id
group by (s.id, c.waste_name);
