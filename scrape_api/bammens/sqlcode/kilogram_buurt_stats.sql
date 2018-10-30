truncate table kilogram_buurtfractiestatweek;

insert into kilogram_buurtfractiestatweek (
	buurt_code,
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
	CONCAT(s.stadsdeel, s.buurt_code),
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
group by (fractie, s.stadsdeel, s.buurt_code, "year", "week");


truncate table kilogram_buurtfractiestatmonth;

insert into kilogram_buurtfractiestatmonth (
	buurt_code,
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
	CONCAT(s.stadsdeel, s.buurt_code),
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
group by (fractie, s.stadsdeel, s.buurt_code, "year", "month");
