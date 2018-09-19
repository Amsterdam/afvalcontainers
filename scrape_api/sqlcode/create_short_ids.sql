/* Create short ids based on (part off) streetcode and housenumber

   If there are multiple sites for street and housenumber add a rownumber
   this is true in ~200 cases. parks, long weird streets with no houses.
*/

update afvalcontainers_site s set
        short_id = short.short_id
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


update afvalcontainers_site s set
        short_id = cast(concat(rown, short.short_id) as int)
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
) as short
where short.rown > 1
and short.site_id = s.id
