DROP TABLE IF EXISTS bgt_clusters;

SELECT DISTINCT
    site_geometrie,
    ST_Centroid(site_geometrie) as centroid,
    round(ST_X(ST_Centroid(site_geometrie))) as x,
    round(ST_Y(ST_Centroid(site_geometrie))) as y
INTO bgt_clusters
FROM (
    SELECT
    ST_ConvexHull(
        ST_CollectionExtract(
            unnest(ST_ClusterIntersecting(
                st_buffer(ba.geometrie, 3.5))), 3)
    ) as site_geometrie
    FROM bgt."BGTPLUS_BAK_afval_apart_plaats" ba
    LEFT JOIN stadsdeel s
        ON ST_Within(ba.geometrie, s.wkb_geometry)
    WHERE s.id is not null
) AS s
