"""
Create cluster id's
"""
import logging
import models

# from sqlalchemy.sql import select
# from sqlalchemy import bindparam

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
SELECT DISTINCT w.id, b.ogc_fid, b.geometrie
from afvalcontainers_well w
left join {bgt_table} b on(st_dwithin(b.geometrie, w.geometrie, 0.0004))
where b.ogc_fid is not null
"""


BGT_TABLES = [
    ('bgt."BGTPLUS_BAK_afval_apart_plaats"', 'MultiPoint'),
    ('bgt."BGT_WGL_voetpad"', 'MultiPolygon'),
    ('bgt."BGT_WGL_voetgangersgebied"', 'MultiPolygon'),
    ('bgt."BGT_WGL_fietspad"', 'MultiPolygon'),
    ('bgt."BGT_WGL_parkeervlak"', 'MultiPolygon'),
    ('bgt."BGT_WGL_rijbaan_lokale_weg"', 'MultiPolygon'),
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


WELL_BGT_MAP = {}


def store_results(results):
    for row in results:
        new = {'id': row[0], 'o': row[1], 'data': data}


def collect_bgt_for_wells():
    """
    For every well collect BGT items
    """

    for bgt_table, _geo_type in BGT_TABLES:
        f_bgt_dwithin = BGT_DWITHIN.format(bgt_table=bgt_table)
        results = session.execute(f_bgt_dwithin)


def main():
    convert_tables_4326()


if __name__ == "__main__":
    """
    """
    engine = models.make_engine()
    session = models.set_session(engine)
    main()
    session.close()
