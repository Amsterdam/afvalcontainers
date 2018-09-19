DROP TABLE IF EXISTS well_nobgt_clusters;

SELECT DISTINCT
    site_geometrie,
    ST_Centroid(site_geometrie) as centroid,
    round(ST_X(ST_Centroid(site_geometrie))) as x,
    round(ST_Y(ST_Centroid(site_geometrie))) as y
INTO well_nobgt_clusters
FROM (
    SELECT
    ST_ConvexHull(
        ST_CollectionExtract(
            unnest(ST_ClusterIntersecting(
                st_buffer(w.geometrie_rd, 8))), 3)
    ) as site_geometrie
    FROM afvalcontainers_well w
    WHERE site_id is null
    AND w.active = true
    AND EXISTS (select well_id from afvalcontainers_container c where w.id = c.well_id)
) AS s
