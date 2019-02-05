"""Create Sites with short ID's.

Sites are collection of wells containing containers.

-They change every day in container content.
-New wells are added / removed daily.
-A short ID is used for coupling sites with kilogram measurements.

The clustering of wells into sites is a rather complex issue.


active 0 = inactive
active 1 = active
active 2 = future active
"""

import logging
import models
import argparse
import os
import overlapping_sites

from sqlalchemy import func
# from sqlalchemy.sql import select
from sqlalchemy import bindparam
from validation import validate_attribute_counts

log = logging.getLogger(__name__)


# TRANSFORM_4326 = """
# ALTER TABLE {tablename}
#  ALTER COLUMN geometrie TYPE geometry({geo_type},4326)
#   USING ST_Transform(geometrie,4326);
# """

TRANSFORM_28992 = """
UPDATE afvalcontainers_well wt
SET geometrie_rd = ST_Transform(w.geometrie, 28992)
FROM afvalcontainers_well w
WHERE w.geometrie_rd is null
AND w.geometrie is not null
AND wt.id = w.id
"""

INDEX_SQL = """
create index on {bgt_table} using gist(geometrie);
"""

BGT_COLLECTION = """
select ogc_fid, bgt_type, geometrie
into bgt_collection
from {source_table}
"""

BGT_DWITHIN = """
SELECT
    w.id,
    w.geometrie_rd,
    b.identificatie_lokaalid,
    ST_AsText(b.geometrie),
    ST_DISTANCE(w.geometrie_rd, b.geometrie),
    GeometryType(b.geometrie)
FROM afvalcontainers_well w
LEFT JOIN {bgt_table} b
ON (st_dwithin(b.geometrie, w.geometrie_rd, {distance}))
WHERE b.ogc_fid IS NOT null
"""

CREATE_PAND_DISTANCE_TO_WELL = """
DROP table IF EXISTS pand_distance_to_well;
SELECT
    p.ogc_fid,
    p.wkb_geometry,
    ST_Distance(well.geometrie_rd, p.wkb_geometry),
    well.id
INTO pand_distance_to_well
FROM pand p
CROSS JOIN LATERAL
    (SELECT
        w.id,
        w.geometrie_rd
     FROM afvalcontainers_well w
     ORDER BY
        w.geometrie_rd <-> p.wkb_geometry
     LIMIT 1) AS well
"""

CREATE_PAND_DISTANCE_TO_FRACTION = """
DROP table IF EXISTS pand_distance_to_{fraction};
SELECT
    p.ogc_fid,
    p.wkb_geometry,
    ST_Distance(well.geometrie_rd, p.wkb_geometry),
    well.id
INTO pand_distance_to_{fraction}
FROM pand p
CROSS JOIN LATERAL
    (SELECT
        w.id,
        w.geometrie_rd
     FROM afvalcontainers_well w, afvalcontainers_container c
     WHERE w.id = c.well_id
     AND c.waste_name = '{fraction}'
     AND c.active = 1
     ORDER BY
        w.geometrie_rd <-> p.wkb_geometry
     LIMIT 1) AS well
"""


# CREATE_WELL_BGT = """
# CREATE TABLE public.well_bgt (
#         id int4 NULL,
#         ogc_fid int4 NULL,
#         geometrie geometry NULL
# )
# WITH (
#     OIDS=FALSE
# );
# """

FOUR_METER = '4'
ON_TOP = '1'

BGT_TABLES = [
    ('bgt."BGTPLUS_BAK_afval_apart_plaats"', 'MultiPoint', ON_TOP),
    ('bgt."BGT_WGL_voetpad"', 'MultiPolygon', ON_TOP),
    ('bgt."BGT_WGL_voetgangersgebied"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_WGL_woonerf"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_OTRN_open_verharding"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_OTRN_transitie"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_OWGL_berm"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_WGL_fietspad"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_WGL_parkeervlak"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_WGL_rijbaan_lokale_weg"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_OTRN_erf"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_BTRN_groenvoorziening"', 'MultiPolygon', FOUR_METER),
    ('bgt."BGT_OTRN_onverhard"', 'MultiPolygon', FOUR_METER),
]


WELL_POINT_MAP = {}
WELL_BGT_MAP = {}

BGT_WELL_MAP = {}
BGT_GEOMETRY_MAP = {}


def map_results(results):
    """Map results. Map wells to bgt objects."""
    for row in results:
        # 'bgt': row[1], 'geom': row[2]}
        well_id = row[0]
        well_point = row[1]
        bgt = row[2]
        bgt_geom = row[3]

        # store bgt info with well
        bgts = WELL_BGT_MAP.setdefault(well_id, [])
        bgts.append((bgt, bgt_geom))
        bgts.sort()

        WELL_POINT_MAP[well_id] = well_point

    log.debug('WELLS matched %d', len(WELL_BGT_MAP))


def make_bgt_geom_map():
    for w_id, bgts in WELL_BGT_MAP.items():
        # bgt_key = "-".join([str(_id) for _id, _ in bgts])

        # bgt_well = BGT_WELL_MAP.setdefault(bgt_key, [])
        # bgt_well.append(w_id)

        bgt_geoms = []
        for bgt_id, geometrie in bgts:
            bgt_geoms.append(geometrie)

        BGT_GEOMETRY_MAP[w_id] = bgt_geoms

    log.debug('BGTS matched %d', len(BGT_GEOMETRY_MAP))


def create_well_bgt_geometry_table():
    """Store well information with bgt information.

    creates records for each bgt item close to a well_id.
    so each well should have around ~8 items nearby.
    """
    conn = engine.connect()
    db_model = models.WellBGT

    bgt_items = []
    bgt_bak_items = []

    for key, bgts in WELL_BGT_MAP.items():
        point = WELL_POINT_MAP[key]

        for bgt_id, geom in bgts:
            bgt_geo = geom
            new = {
                'well_id': key,
                'geometrie': point,
            }

            if geom.startswith('MULTIPOINT'):
                new['bgt_bak'] = bgt_geo
                bgt_bak_items.append(new)
            else:
                new['bgt'] = bgt_geo
                bgt_items.append(new)

    if not bgt_items:
        raise ValueError("nothing matched..")

    insert_stmt = (
        db_model.__table__.insert()
        .values(
            bgt=func.ST_GeomFromText(bindparam('bgt'), 28992)
        )
    )
    conn.execute(insert_stmt, bgt_items)

    if not bgt_bak_items:
        raise ValueError("nothing matched..")

    insert_stmt = (
        db_model.__table__.insert()
        .values(
            bgt_bak=func.ST_Dump(
                func.ST_GeomFromText(bindparam('bgt_bak'), 28992)).geom
        )
    )

    conn.execute(insert_stmt, bgt_bak_items)


def collect_bgt_for_wells():
    """For every well collect BGT items."""
    log.info('Matching wells with BGT.')

    # make sure we have an rd coordinate.

    for bgt_table, geo_type, distance in BGT_TABLES:
        log.debug('Working on %s %s %s', bgt_table, geo_type, distance)
        index_sql = INDEX_SQL.format(bgt_table=bgt_table)
        results = session.execute(index_sql)
        f_bgt_dwithin = BGT_DWITHIN.format(
            bgt_table=bgt_table, distance=distance)
        results = session.execute(f_bgt_dwithin)
        map_results(results)

    # make_bgt_geom_map()
    # session.commit()
    create_well_bgt_geometry_table()


SITE_ID_NULL = "UPDATE afvalcontainers_well SET site_id = NULL"
TRUNCATE_SITE_TABLE_FRACTIES = """
TRUNCATE TABLE afvalcontainers_sitefractie;
TRUNCATE TABLE kilogram_sitefractiestatweek;
TRUNCATE TABLE kilogram_sitefractiestatmonth;
"""


DELETE_SITES_IN = """
DELETE FROM "afvalcontainers_site"
WHERE "afvalcontainers_site"."id"
IN (select id from afvalcontainers_site);
"""


def delete_sites():
    log.info('Clear old sites if they exist')
    session.execute(SITE_ID_NULL)
    session.execute(DELETE_SITES_IN)
    session.execute(TRUNCATE_SITE_TABLE_FRACTIES)
    session.commit()


def fill_rd_geometry():
    """If well have geometrie and no rd geometry add it."""
    session.execute(TRANSFORM_28992)
    session.commit()


# bgt has plus information which is not complete
# but should match with afvalcontainers/wells. if it does not
# we should report this back adding these attributes allow the api to
# report back missing wells.


UPDATE_WELL_NO_BGT_AFVAL = """
UPDATE afvalcontainers_well wt
SET "extra_attributes" = jsonb_set(
        wt."extra_attributes", '{missing_bgt_afval}', to_jsonb(true), true)
FROM afvalcontainers_well w
LEFT JOIN bgt."BGTPLUS_BAK_afval_apart_plaats" ap
     ON (ST_DWithin(w.geometrie_rd, ap.geometrie, 1))
WHERE ap.identificatie_lokaalid is null
AND wt.id = w.id
"""

UPDATE_WELL_IN_WEG = """
UPDATE afvalcontainers_well wt
SET
    "extra_attributes" = jsonb_set(
        wt."extra_attributes", '{in_wegdeel}', to_jsonb(true), true)
FROM afvalcontainers_well w
LEFT JOIN bgt."BGT_WGL_rijbaan_lokale_weg" wd
     ON (ST_Within(w.geometrie_rd, wd.geometrie))
WHERE
    wd.identificatie_lokaalid IS NOT NULL
    AND wt.id = w.id
"""

UPDATE_WELL_IN_PAND = """
UPDATE afvalcontainers_well wt
SET "extra_attributes" =
    jsonb_set(wt."extra_attributes", '{in_pand}', to_jsonb(true), true)
FROM afvalcontainers_well w
LEFT JOIN pand p ON (ST_Within(w.geometrie_rd, p.wkb_geometry))
WHERE p.ogc_fid IS NOT NULL
AND wt.id = w.id
"""

UPDATE_WELL_IN_BGT_SITE = """
UPDATE afvalcontainers_well wt
wt.site_id = s.id
FROM afvalcontainers_well w
LEFT JOIN pand p ON (ST_Within(w.geometrie_rd, p.wkb_geometry))
WHERE p.ogc_fid IS NOT NULL
AND wt.id = w.id
"
"""

CREATE_BGT_CLUSTERS = """
DROP TABLE IF EXISTS bgt_clusters;

SELECT DISTINCT
    site_geometrie,
    ST_Centroid(site_geometrie) as centroid,
    round(ST_X(ST_Centroid(site_geometrie))) as x,
    round(ST_Y(ST_Centroid(site_geometrie))) as y
INTO bgt_clusters
FROM (
    ST_ConvexHull(
        ST_CollectionExtract(
            unnest(ST_ClusterIntersecting(
                st_buffer(ba.geometrie, 8))), 3)
    ) as site_geometrie
    FROM bgt."BGTPLUS_BAK_afval_apart_plaats" ba
    LEFT JOIN stadsdeel s
        ON ST_Within(ba.geometrie, s.wkb_geometry)
    WHERE s.id is not null
) AS s
"""

COPY_CLUSTERS_TO_API = """
INSERT INTO afvalcontainers_site
SELECT
    Concat(x, '-', y) as id,
    ST_Transform(
        ST_Centroid(site_geometrie), 28992) as centroid
    site_geometrie as geometrie
FROM bgt_clusters
LEFT JOIN stadsdeel s on ST_Within(ba.geometrie, s.wkb_geometry)
"""


WASTE_DESCRIPTIONS = (
    ("Rest"),
    ("Glas"),
    ("Papier"),
    ("Textiel"),
    ("Wormen"),
    ("Plastic"),
    ("KCA"),
)


def create_pand_distance():
    session.execute(CREATE_PAND_DISTANCE_TO_WELL)
    session.commit()
    for fraction in WASTE_DESCRIPTIONS:
        log.info('Distance for %s', fraction)
        sql = CREATE_PAND_DISTANCE_TO_FRACTION.format(
            fraction=fraction)
        session.execute(sql)
        session.commit()


def execute_sqlfile(filename):
    with open(os.path.join('bammens', filename)) as sqltxt:
        statements = sqltxt.read()
        session.execute(statements)
        session.commit()


"""
   Calculate capacity using

   conversion from kg to m3.
"""

CAPACITY_SQL = """
UPDATE {table} t set
    capacity=t."sum"::float / {kgm3}::float / t.volume::float
WHERE t.sum > 0
AND t.volume > 0
AND t.fractie = '{fractie}';
"""


KG_VOLUME_CONVERSION = {
    'Rest': 100,
    'Papier': 70,
    'Glas': 300,
    'Plastic': 25,
    'Kunststof': 25,
    'Textiel': 120,
    'GFT': 400,
}


def fill_kilo_stats_table():
    log.info('create weekly / monthly buurt statistics')
    execute_sqlfile('sqlcode/kilogram_buurt_stats.sql')

    log.info('create weekly / monthly site statisics')
    execute_sqlfile('sqlcode/kilogram_site_stats.sql')

    log.info('add buurt bewoners counts to measurements')
    execute_sqlfile('sqlcode/bbga_buurt.sql')

    log.info('add volume capacity to site measurements')
    execute_sqlfile('sqlcode/capacity_to_sitestats.sql')

    tables = [
        'kilogram_sitefractiestatweek',
        'kilogram_sitefractiestatmonth',
    ]

    for table in tables:
        for fractie, kgm3 in KG_VOLUME_CONVERSION.items():
            sqlcap = CAPACITY_SQL.format(
                table=table, fractie=fractie, kgm3=kgm3
            )
            print(sqlcap)
            session.execute(sqlcap)
            session.commit()


def merge_overlapping_sites():

    bgt_tables = [
        '"bgt"."BGT_OWGL_berm"',
        '"bgt"."BGT_WGL_voetpad"',
        '"bgt"."BGT_BTRN_groenvoorziening"',
    ]

    execute_sqlfile('sqlcode/merge_overlapping_sites.sql')

    for table in bgt_tables:
        log.info('Sites in same BGT %s', table)
        index_sql = INDEX_SQL.format(bgt_table=table)
        session.execute(index_sql)
        fix_overlap = overlapping_sites.BGT_OVERLAP_SQL
        fix_overlap = fix_overlap.format(bgt_table=table)
        session.execute(fix_overlap)
        session.commit()


def create_site_clusters():
    """
    Cluster wells that should be together.

    # TIP when developing comment out the sql that was ok.
    all instructions should be idempotent.
    """
    log.info('Create BGT based sites')
    delete_sites()
    # create new bgt bases clusters
    execute_sqlfile('sqlcode/create_bgt_clusters.sql')
    # match with current containers
    log.info('Link containers with BGT sites ')
    execute_sqlfile('sqlcode/create_sites_from_bgt.sql')
    # match wells with bgt locations
    log.info('Update wells with site_id with BGT sites')
    execute_sqlfile('sqlcode/update_well_site_id.sql')
    # Create clusters of left containers
    log.info('Create sites with leftover wells')
    execute_sqlfile('sqlcode/create_well_cluster.sql')
    execute_sqlfile('sqlcode/create_sites_from_well_clusters.sql')

    # merge overlapping sites
    execute_sqlfile('sqlcode/merge_overlapping_sites.sql')
    merge_overlapping_sites()

    # match left over wells with clusters
    log.info('Update wells with site_id')
    log.info('Overlapping sites have been removed')
    execute_sqlfile('sqlcode/update_well_site_id.sql')

    log.info('Improve streetnames with lig_plaatsen')
    execute_sqlfile('sqlcode/update_site_address_with_ligplaats.sql')

    log.info('Improve streetnames with vbo < 20 and 60 meter improvement')
    execute_sqlfile('sqlcode/update_site_address_with_vbo.sql')

    log.info('Add short codes based on streetcode and number')
    execute_sqlfile('sqlcode/create_short_ids.sql')


def site_fracties():
    log.info('Fill site container fracties')
    execute_sqlfile('sqlcode/site_fracties.sql')


def buurt_container_counts():
    log.info('Fill kilo buurt container counts')
    execute_sqlfile('sqlcode/container_counts_to_buurtstats.sql')


def update_quality_in_extra_attributes():
    """Add some quality indicators to well items."""
    qa_sql = [
        ('in_pand', UPDATE_WELL_IN_PAND),
        ('in_weg', UPDATE_WELL_IN_WEG),
        ('no_bgt', UPDATE_WELL_NO_BGT_AFVAL),
    ]

    for topic, sql_item in qa_sql:
        log.info('Add "%s" to extra_attributes', topic)
        session.execute(sql_item)
        session.commit()


DROP_OLD_TABLES = """
DROP table if exists bag_verblijfsobject;
DROP table if exists bag_ligplaats;
DROP table if exists bag_standplaats;
DROP table if exists bgt_clusters;
"""


def drop_unrelevant_data():
    """Clean all extra data no longer needed.

    When import is done data not needed
    in API is removed to keep backups small.
    """

    drop_sql = [
        ('bag', DROP_OLD_TABLES),
        ('bgt', "DROP SCHEMA bgt CASCADE"),
    ]

    for topic, sql_item in drop_sql:
        log.info(sql_item)
        session.execute(sql_item)
        session.commit()


VALIDATE_SQL = [
    ("""select count(*) from afvalcontainers_well
        where stadsdeel is null""", 0, 5),
    ("""select count(*) from afvalcontainers_well
        where buurt_code is null""", 0, 5),

    ("""select count(*) from afvalcontainers_well
        where extra_attributes->'missing_bgt_afval' = 'true'""",
        0, 5000),

    ("""select count(*) from afvalcontainers_site
        where bgt_based is true""",
        8000, 15000),

    ("""select count(*) from afvalcontainers_well
        where site_id is null""",
        0, 315),

    ("""select count(*) from afvalcontainers_site
        where short_id is null""",
        0, 35),
]


def main(args):  # noqa
    if args.merge_bgt:
        collect_bgt_for_wells()
    if args.validate:
        validate_attribute_counts(VALIDATE_SQL, session)
    if args.qa_wells:
        update_quality_in_extra_attributes()
    if args.clusters:
        create_site_clusters()
    if args.pand_distance:
        create_pand_distance()
    if args.fill_rd:
        fill_rd_geometry()
    if args.kilostats:
        fill_kilo_stats_table()
    if args.sitefracties:
        site_fracties()
    if args.buurtcontainercounts:
        buurt_container_counts()
    if args.cleanextra:
        drop_unrelevant_data()


if __name__ == "__main__":
    desc = "Merge wells with BGT and create sites"
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--fill_rd",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Add RD geometry to wells",
    )

    inputparser.add_argument(
        "--merge_bgt",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Merge Wells with BGT objects",
    )

    inputparser.add_argument(
        "--qa_wells",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Quality Analysis Wells",
    )

    inputparser.add_argument(
        "--clusters",
        default=False,
        action="store_true",
        help="Create clusters of wells",
    )

    inputparser.add_argument(
        "--pand_distance",
        default=False,
        action="store_true",
        help="Create pand distance table",
    )

    inputparser.add_argument(
        "--create_views",
        default=False,
        action="store_true",
        help="Create pand distance table",
    )

    inputparser.add_argument(
        "--validate",
        default=False,
        action="store_true",
        help="validate counts",
    )

    inputparser.add_argument(
        "--sitefracties",
        default=False,
        action="store_true",
        help="store site fracties",
    )

    inputparser.add_argument(
        "--buurtcontainercounts",
        default=False,
        action="store_true",
        help="add counts to buurten",
    )

    inputparser.add_argument(
        "--kilostats",
        default=False,
        action="store_true",
        help="create weekly/monthly kilogram.nl stats for site",
    )

    inputparser.add_argument(
        "--cleanextra",
        default=False,
        action="store_true",
        help="Clear database of BGT / BAG",
    )

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()
    engine = models.make_engine()
    session = models.set_session(engine)
    main(args)
    session.close()
