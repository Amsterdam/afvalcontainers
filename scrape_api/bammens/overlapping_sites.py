
BGT_OVERLAP_SQL = """
update afvalcontainers_site ts set
        geometrie=newgeo,
        active=5
from (
    select a.id,
    st_convexhull(st_union(a.geometrie, b.geometrie)) newgeo,
    vp1.ogc_fid
    from afvalcontainers_site a, afvalcontainers_site b,
    {bgt_table} vp1, {bgt_table} vp2
    where a.id != b.id
    and st_dwithin(a.geometrie, b.geometrie, 5)
    and st_dwithin(st_centroid(a.geometrie), vp1.geometrie, 0)
    and st_dwithin(st_centroid(b.geometrie), vp2.geometrie, 0)
    and vp1.ogc_fid = vp2.ogc_fid
    and a.id > b.id
) overlap
where overlap.id = ts.id;

delete from afvalcontainers_site
where id=any(
    select a.id
    from afvalcontainers_site a, afvalcontainers_site b,
    {bgt_table} vp1, {bgt_table} vp2
    where a.id != b.id
    and st_dwithin(a.geometrie, b.geometrie, 5)
    and st_dwithin(st_centroid(a.geometrie), vp1.geometrie, 0)
    and st_dwithin(st_centroid(b.geometrie), vp2.geometrie, 0)
    and vp1.ogc_fid = vp2.ogc_fid
    and a.id < b.id
);
"""
