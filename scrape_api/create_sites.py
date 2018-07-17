"""
Create cluster id's
"""
import logging
import models
import argparse

from sqlalchemy import func
# from sqlalchemy.sql import select
from sqlalchemy import bindparam

log = logging.getLogger(__name__)


# bgt."BGT_WGL_rijbaan_lokale_weg

TRANSFORM_4326 = """
ALTER TABLE {tablename}
 ALTER COLUMN geometrie TYPE geometry({geo_type},4326)
  USING ST_Transform(geometrie,4326);
"""

BGT_COLLECTION = """
select ogc_fid, bgt_type, geometrie
into bgt_collection
from {source_table}
"""

BGT_DWITHIN = """
SELECT
    w.id, w.geometrie, b.identificatie_lokaalid, b.geometrie,
    ST_DISTANCE(w.geometrie, b.geometrie)
FROM afvalcontainers_well w
LEFT JOIN {bgt_table} b ON (st_dwithin(b.geometrie, w.geometrie, 0.00004))
WHERE b.ogc_fid IS NOT null
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

BGT_TABLES = [
    ('bgt."BGTPLUS_BAK_afval_apart_plaats"', 'MultiPoint'),
    ('bgt."BGT_WGL_voetpad"', 'MultiPolygon'),
    ('bgt."BGT_WGL_voetgangersgebied"', 'MultiPolygon'),
    ('bgt."BGT_WGL_woonerf"', 'MultiPolygon'),
    ('bgt."BGT_OTRN_open_verharding"', 'MultiPolygon'),
    ('bgt."BGT_OTRN_transitie"', 'MultiPolygon'),
    ('bgt."BGT_OWGL_berm"', 'MultiPolygon'),
    ('bgt."BGT_WGL_fietspad"', 'MultiPolygon'),
    ('bgt."BGT_WGL_parkeervlak"', 'MultiPolygon'),
    ('bgt."BGT_WGL_rijbaan_lokale_weg"', 'MultiPolygon'),
    ('bgt."BGT_OTRN_erf"', 'MultiPolygon'),
    ('bgt."BGT_BTRN_groenvoorziening"', 'MultiPolygon'),
    ('bgt."BGT_OTRN_onverhard"', 'MultiPolygon'),
    ('bgt."BGT_OTRN_onverhard"', 'MultiPolygon'),
]


def convert_tables_4326():
    for bgt_table, geo_type in BGT_TABLES:
        log.debug('Converting %s %s', bgt_table, geo_type)
        f_convert = TRANSFORM_4326.format(
            tablename=bgt_table,
            geo_type=geo_type
        )
        session.execute(f_convert)
        session.commit()


WELL_POINT_MAP = {}
WELL_BGT_MAP = {}
BGT_WELL_MAP = {}
BGT_GEOMETRY_MAP = {}


def map_results(results):
    """
    map results. map wells to bgt objects
    """
    for row in results:
        # 'bgt': row[1], 'geom': row[2]}
        well_id = row[0]
        well_point = row[1]
        bgt = row[2]
        bgt_geom = row[3]
        bgts = WELL_BGT_MAP.setdefault(well_id, [])
        bgts.append((bgt, bgt_geom))
        bgts.sort()
        WELL_POINT_MAP[well_id] = well_point

    for w_id, bgts in WELL_BGT_MAP.items():
        bgt_key = "-".join([str(_id) for _id, _ in bgts])
        bgt_well = BGT_WELL_MAP.setdefault(bgt_key, [])
        bgt_well.append(well_id)
        bgt_geoms = []
        for bgt_id, geometrie in bgts:
            bgt_geoms.append(geometrie)

        BGT_GEOMETRY_MAP[w_id] = bgt_geoms

    # import q
    # q.d()


def create_well_bgt_geometry_table():
    """
    """
    conn = engine.connect()
    dbitem = models.WellBGT

    insert_items = []

    for key, row in WELL_BGT_MAP.items():
        point = WELL_POINT_MAP[key]
        geometries = BGT_GEOMETRY_MAP[key]
        for geom in geometries:
            new = {
                'well_id': key,
                'geometrie': point,
                'bgt': geom,
            }
            insert_items.append(new)

    insert_stmt = (
        dbitem.__table__.insert()
        .values(
            bgt=func.ST_Multi(bindparam('bgt'))
        )
    )
    conn.execute(insert_stmt, insert_items)


def collect_bgt_for_wells():
    """
    For every well collect BGT items
    """
    log.info('Matching wells with BGT.')
    all_results = []
    for bgt_table, _geo_type in BGT_TABLES:
        f_bgt_dwithin = BGT_DWITHIN.format(bgt_table=bgt_table)
        results = session.execute(f_bgt_dwithin)
        all_results.extend(results)

    map_results(all_results)
    # session.commit()
    create_well_bgt_geometry_table()


# bgt has plus information which is not complete
# but should match with afvalcontainers/wells. if it does not
# we should report this back.
UPDATE_WELL_NO_BGT_AFVAL = """
UPDATE afvalcontainers_well wt
SET "extra_attributes" = jsonb_set(
        wt."extra_attributes", '{missing_bgt_afval}', to_jsonb(true), true)
FROM afvalcontainers_well w
LEFT JOIN bgt."BGTPLUS_BAK_afval_apart_plaats" ap
     ON (ST_DWithin(w.geometrie, ap.geometrie, 0.0008))
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
     ON (ST_Within(w.geometrie, wd.geometrie))
WHERE
    wd.identificatie_lokaalid IS NOT NULL
    AND wt.id = w.id
"""

UPDATE_WELL_IN_PAND = """
UPDATE afvalcontainers_well wt
SET "extra_attributes" =
    jsonb_set(wt."extra_attributes", '{in_pand}', to_jsonb(true), true)
FROM afvalcontainers_well w
LEFT JOIN pand p ON (ST_Within(w.geometrie, p.wkb_geometry))
WHERE p.ogc_fid IS NOT NULL
AND wt.id = w.id
"""


def update_quality_in_extra_attributes():
    """Add some quality indicators to well items
    """
    qa_sql = [
        ('in_pand', UPDATE_WELL_IN_PAND),
        ('in_weg', UPDATE_WELL_IN_WEG),
        ('no_bgt', UPDATE_WELL_NO_BGT_AFVAL),
    ]

    for topic, sql_item in qa_sql:
        log.info('Add "%s" to extra_attributes', topic)
        session.execute(sql_item)
        session.commit()


def main(args):
    if args.convert_4326:
        convert_tables_4326()
    if args.merge_bgt:
        collect_bgt_for_wells()
    if args.qa_wells:
        update_quality_in_extra_attributes()


if __name__ == "__main__":
    """
    """
    desc = "Merge wells with BGT and create sites"
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--convert_4326",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Convert wells to RD",
    )

    inputparser.add_argument(
        "--merge_bgt",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Convert wells to RD",
    )

    inputparser.add_argument(
        "--qa_wells",
        default=False,
        # choices=ENDPOINTS,
        action="store_true",
        help="Quality Analysis Wells",
    )

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()
    engine = models.make_engine()
    session = models.set_session(engine)
    main(args)
    session.close()
