/*

Some SQL used for merge / cleanup of well / container data
used in this project.

Left as inspiration / reference staring point to continue later..
*/

/*
select w.id, w.geometrie, w.placing_date, w.active, w.address->>'summary', w.stadsdeel, w.buurt_code into lonely_well from afvalcontainers_well w
left join well_bgt wb on (w.id = wb.well_id)
where wb.well_id is null


select * from lonely_well l, afvalcontainers_well w, afvalcontainers_container c
where l.id = w.id
and w.id = c.well_id
*/

select w.geometrie, w.placing_date, w.active, w.address->>'summary', w.stadsdeel, w.buurt_code
into no_bgt
from afvalcontainers_well w
left join bgt."BGTPLUS_BAK_afval_apart_plaats" bgt on (ST_DWithin(bgt.geometrie, w.geometrie, 0.00004))
where bgt.identificatie_lokaalid is null


select w.geometrie, w.placing_date, w.active, w.address->>'summary', w.stadsdeel, w.buurt_code , pand.wkb_geometry as pand_geo
into well_in_pand
from afvalcontainers_well w
left join pand on (ST_Within(w.geometrie, pand.wkb_geometry))
where pand.id is not null

update afvalcontainers_well wt
set "extra_attributes" = jsonb_set(wt."extra_attributes", '{in_wegdeel}', to_jsonb(true), true)
from afvalcontainers_well w
left join bgt."BGT_WGL_rijbaan_lokale_weg" wd on (ST_Within(w.geometrie, wd.geometrie))
where wd.identificatie_lokaalid is not null
and wt.id = w.id


update afvalcontainers_well wt
set "extra_attributes" = jsonb_set(wt."extra_attributes", '{in_wegdeel}', to_jsonb(true), true)
from afvalcontainers_well w
left join bgt."BGT_WGL_rijbaan_lokale_weg" wd on (ST_Within(w.geometrie, wd.geometrie))
where wd.identificatie_lokaalid is not null
and wt.id = w.id

/*
update afvalcontainers_well wt
set "extra_attributes" = jsonb_set(wt."extra_attributes", '{missing_bgt_afval}', to_jsonb(true), true)
*/
select distinct count(*)
from afvalcontainers_well w
left join bgt."BGTPLUS_BAK_afval_apart_plaats" ap on (ST_DWithin(w.geometrie, ap.geometrie, 0.00004))
where ap.identificatie_lokaalid is null
/*and wt.id = w.id*/


update afvalcontainers_well wt
set "extra_attributes" = jsonb_set(wt."extra_attributes", '{in_pand}', to_jsonb(true), true)
from afvalcontainers_well w
left join pand p on (ST_Within(w.geometrie, p.wkb_geometry))
where p.ogc_fid is not null
and wt.id = w.id




select * into well from afvalcontainers_well


select bgt.geometrie /*stadsdeel.code, stadsdeel.naam*/
/*into missing_well*/
from bgt."BGTPLUS_BAK_afval_apart_plaats" bgt
left join afvalcontainers_well w on (ST_DWithin(bgt.geometrie, w.geometrie, 0.4))
/*left join stadsdeel on ST_Within(stadsdeel.wkb_geometry, bgt.geometrie)*/
where w.id is null

select bgt.geometrie, stadsdeel.naam, stadsdeel.code, opr.display,
/*into "missing_well3"*/
	(select concat(num."_openbare_ruimte_naam", ' ', num.huisnummer) as adres
	from bag_nummeraanduiding num
	order by bgt.geometrie <#> num."_geom" limit 1
	)
from bgt."BGTPLUS_BAK_afval_apart_plaats" bgt
left join afvalcontainers_well w on (ST_DWithin(w.geometrie, bgt.geometrie, 0.0004))
left join stadsdeel on ST_Within(bgt.geometrie, stadsdeel.wkb_geometry)
left join openbareruimte opr on ST_Within(bgt.geometrie, opr.wkb_geometry)
where w.id is null
and stadsdeel.code is not null

/*left join bag_nummeraanduiding num on (ST_DWithin(bgt.geometrie, num._geom, 0.0004) or ST_DWithin(bgt.geometrie, num._geom, 0.1))*/


ALTER TABLE bag_nummeraanduiding
 ALTER COLUMN _geom TYPE geometry('Geometry',4326)
  USING ST_Transform(_geom,4326);
