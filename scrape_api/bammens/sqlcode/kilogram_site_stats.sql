truncate table afvalcontainers_sitefractiestat;

insert into afvalcontainers_sitefractiestat (
	site_id,
	fractie,
	"week",
	"year",
	wegingen,
	"sum",
	"min",
	"max",
	"avg",
	"stddev"
) select
	site_id,
	fractie,
	EXTRACT(WEEK from weigh_at)::int as "week",
	EXTRACT(YEAR from weigh_at)::int as "year",
	count(*) wegingen,
	sum(net_weight),
	min(net_weight),
	max(net_weight),
	ceil(avg(net_weight)) "avg",
	ceil(stddev(net_weight)) "stddev"
from kilogram_weigh_measurement m, afvalcontainers_site s
where m.site_id = s.short_id
and m.valid
group by (fractie, site_id, "year", "week")
