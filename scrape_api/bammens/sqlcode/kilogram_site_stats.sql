truncate table kilogram_sitefractiestatweek;

insert into kilogram_sitefractiestatweek (
	site_id,
	fractie,
	"week",
	"year",
	measurements,
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
	count(*) measurements,
	sum(net_weight),
	min(net_weight),
	max(net_weight),
	ceil(avg(net_weight)) "avg",
	ceil(stddev(net_weight)) "stddev"
from kilogram_weigh_measurement m, afvalcontainers_site s
where m.site_id = s.short_id
and m.valid
group by (fractie, site_id, "year", "week");


truncate table kilogram_sitefractiestatmonth;

insert into kilogram_sitefractiestatmonth (
	site_id,
	fractie,
	"month",
	"year",
	measurements,
	"sum",
	"min",
	"max",
	"avg",
	"stddev"
) select
	site_id,
	fractie,
	EXTRACT(MONTH from weigh_at)::int as "month",
	EXTRACT(YEAR from weigh_at)::int as "year",
	count(*) measurements,
	sum(net_weight),
	min(net_weight),
	max(net_weight),
	ceil(avg(net_weight)) "avg",
	ceil(stddev(net_weight)) "stddev"
from kilogram_weigh_measurement m, afvalcontainers_site s
where m.site_id = s.short_id
and m.valid
group by (fractie, site_id, "year", "month");
