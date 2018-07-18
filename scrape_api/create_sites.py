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
    w.id, w.geometrie, b.identificatie_lokaalid, ST_AsText(b.geometrie),
    ST_DISTANCE(w.geometrie, b.geometrie),
    GeometryType(b.geometrie)
FROM afvalcontainers_well w
LEFT JOIN {bgt_table} b ON (st_dwithin(b.geometrie, w.geometrie, {distance}))
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

FOUR_METER = '0.000089'
ON_TOP = '0.000009'

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


def convert_tables_4326():
    for bgt_table, geo_type, _distance in BGT_TABLES:
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
    """
    """
    conn = engine.connect()
    db_model = models.WellBGT

    bgt_items = []
    bgt_bak_items = []

    for key, bgts in WELL_BGT_MAP.items():
        point = WELL_POINT_MAP[key]
        # geometries = BGT_GEOMETRY_MAP[key]

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
                new['bgt'] = bgt_geo,
                bgt_items.append(new)

    insert_stmt = (
        db_model.__table__.insert()
        .values(
            bgt=func.ST_GeomFromText(bindparam('bgt'), 4326)
        )
    )
    conn.execute(insert_stmt, bgt_items)

    insert_stmt = (
        db_model.__table__.insert()
        .values(
            bgt_bak=func.ST_Dump(
                func.ST_GeomFromText(bindparam('bgt_bak'), 4326)).geom
        )
    )

    conn.execute(insert_stmt, bgt_bak_items)


def collect_bgt_for_wells():
    """
    For every well collect BGT items
    """
    log.info('Matching wells with BGT.')

    for bgt_table, geo_type, distance in BGT_TABLES:
        log.debug('Working on %s %s %s', bgt_table, geo_type, distance)
        f_bgt_dwithin = BGT_DWITHIN.format(
            bgt_table=bgt_table, distance=distance)
        results = session.execute(f_bgt_dwithin)
        map_results(results)

    # make_bgt_geom_map()
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
