/* Create short ids based on (part off) streetcode and housenumber

   If there are multiple sites for street and housenumber add a rownumber
   this is true in ~200 cases. which could happend in parks and
   long weird streets with no houses.

   Also copy adress summary information / chauffeur instructions to the site.
*/

/*

	Create short id for most common case.

	For each site, find one well (cross join) ,
	and join with opr / openbare ruimte on the straatnaam.

	now we have all information to crate a short id.

	rown must be 1. so in case multiple sites share the same adress
	we take only the first one.

*/

update afvalcontainers_site s set
        short_id = short.short_id,
        extra_attributes = jsonb_build_object('chauffeur', short.chauffeur)
from (
select
    row_number() over (partition by s.straatnaam, s.huisnummer order by s.id) as rown,
    cast(
      concat(
        right(o.id, 5),
        huisnummer
    ) as int) as short_id,
    s.id as site_id,
    straatnaam,
    huisnummer,
    distance,
    o.id as code,
    case bgt_based
        when bgt_based=true then 1
        else 2
    end as bgt_based,
    w.address->>'summary' as chauffeur
from afvalcontainers_site s
left outer join openbareruimte o on(s.straatnaam = o.display)
cross join lateral (select * from afvalcontainers_well w where s.id = w.site_id limit 1) as w
where o.opr_type = 'Weg'
) as short
where short.rown = 1 and short.site_id = s.id;

/*

	Same as above but now we do all left over cases in which
	sites SHARE the same streetnamen and housenumber.

	In this case where rownumber > 1 we add the rownumber to the short id
	assuming this will be unique.

*/


update afvalcontainers_site s set
        short_id = cast(concat(rown, short.short_id) as int),
        extra_attributes = jsonb_build_object('chauffeur', short.chauffeur)
from (
select
    row_number() over (partition by s.straatnaam, s.huisnummer order by s.id) as rown,
    concat(
        right(o.id, 4),
        huisnummer
    ) as short_id,
    s.id as site_id,
    straatnaam,
    huisnummer,
    distance,
    o.id as code,
    w.address->>'summary' as chauffeur
from afvalcontainers_site s
left outer join openbareruimte o on(s.straatnaam = o.display)
cross join lateral (select * from afvalcontainers_well w where s.id = w.site_id limit 1) as w
where o.opr_type = 'Weg'
and s.short_id is null
) as short
where short.rown > 1
and short.site_id = s.id;


/*

Some sites have no well. We still want to create a short id for them.

*/

update afvalcontainers_site s set
	short_id = cast(concat(rown, short.short_id) as int)
from (
select
    row_number() over (partition by s.straatnaam, s.huisnummer order by s.id) as rown,
    concat(
	right(o.id, 5),
	huisnummer
    ) as short_id,
    s.id as site_id,
    straatnaam,
    huisnummer,
    distance,
    o.id as code
from afvalcontainers_site s
left outer join openbareruimte o on(s.straatnaam = o.display)
where o.opr_type = 'Weg'
and s.short_id is null
) as short
where short.site_id = s.id;


/*

	Some sites are missing an OPR with valid numbers

	5 cases in molenwijk. (the building is the actual street.)

	In this case we take nearest opr + housenumer rownumber > 1 we add the rownumber to the short id
	assuming this will be unique.

*/

update afvalcontainers_site s set
        short_id = cast(concat(rown, short.short_id) as int),
        extra_attributes = jsonb_build_object('chauffeur', short.chauffeur)
from (
select
    row_number() over (partition by opr.display, s.huisnummer order by s.id) as rown,
    concat(
        right(opr.id, 4),
        huisnummer
    ) as short_id,
    s.id as site_id,
    straatnaam,
    huisnummer,
    distance,
    opr.id as code,
    w.address->>'summary' as chauffeur
from afvalcontainers_site s
cross join lateral (select * from afvalcontainers_well w where s.id = w.site_id limit 1) as w
cross join lateral
	(select
		o.id,
		o.display
	from openbareruimte o, bag_verblijfsobject v
	where o.opr_type = 'Weg'
	order by
		o.wkb_geometry <-> s.geometrie
	limit 1) as opr
) as short
where short.site_id = s.id
and s.short_id is null;
