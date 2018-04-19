"""
Copy raw data into django api models
"""

import random
import argparse
import models
import logging
from sqlalchemy.sql import select
from sqlalchemy import bindparam

log = logging.getLogger(__name__)


INSERT_WELLS = """
INSERT INTO afvalcontainers_well (
    id,
    serial_number,
    id_number,
    owner,
    created_at,
    warranty_date,
    operational_date,
    placing_date,
    active,
    geometrie,
    address
)
SELECT
    id,
    data->>'serial_number' as serial_number,
    data->>'id_number' as id_number,
    CAST(data->>'owner' as jsonb) as owner,
    CAST(data->>'created_at' as timestamp) as created_at,
    CAST(data->>'warranty_date' as timestamp) as warranty_date,
    CAST(data->>'placing_date' as timestamp) as placing_date,
    CAST(data->>'operational_date' as timestamp) as operational_date,
    CAST(data->>'active' as bool) as active,
    ST_SetSRID(
        ST_POINT(
            CAST(data->'location'->'position'->>'longitude' as float),
            CAST(data->'location'->'position'->>'latitude' as float)
        ), 4326) as geometrie,
    CAST(data->'location'->>'address' as jsonb) as address
    FROM bammens_well_raw;
"""  # noqa


INSERT_CONTAINERS = """


"""


INSERT_TYPES = """
INSERT INTO afvalcontainers_containertype
SELECT id, name, CAST("data"->>'volume' as INT)
FROM bammens_containertypes_raw
"""


def update_types():
    sql = INSERT_TYPES
    session.execute("TRUNCATE TABLE afvalcontainers_well;")
    session.execute(sql)
    session.commit()


# session.commit()


def update_containers():
    sql = INSERT_CONTAINERS
    session.execute("TRUNCATE TABLE afvalcontainers_container;")
    session.execute(sql)
    session.commit()


def update_wells():
    insert = INSERT_WELLS
    session.execute("TRUNCATE TABLE afvalcontainers_well")
    session.execute(insert)
    session.commit()


def validate_timestamps(item):
    """We recieve invalid timestamps
    so we clean them up here.
    """
    timestamp_keys = (
        "created_at",
        "placing_date",
        "warranty_date",
        "operational_date")

    for key in timestamp_keys:
        date = item.get(key)
        if not date:
            continue

        invalid = False
        # d2 = dateparser.parse(date)
        # d = parser.parse(date)
        if date.startswith('000'):
            invalid = True
        elif date.startswith('-0'):
            invalid = True
        elif date.startswith('-10'):
            invalid = True
        if invalid:
            log.error("Invalid %s %s %s", key, date, item["id"])
            item[key] = None

    return item


def cleanup_dates(endpoint):
    """
    If some bad dates slipped into the
    json. We can clean it up.
    """
    conn = engine.connect()
    dbitem = models.ENDPOINT_MODEL[endpoint]

    s = select([dbitem])
    results = conn.execute(s)
    cleaned = []
    for row in results:
        data = validate_timestamps(row[2])
        new = {'id': row[0], 'scraped_at': row[1], 'data': data}
        cleaned.append(new)

    upd_stmt = (
        dbitem.__table__.update()
        .where(dbitem.id == bindparam('id'))
        .values(id=bindparam('id'))
    )
    conn.execute(upd_stmt, cleaned)


OPTIONS = {
    "container_types": update_types,
    "containers": update_containers,
    "wells": update_wells,
}


def main():
    if args.cleanup:
        if args.endpoint:
            endpoint = args.endpoint[0]
            cleanup_dates(endpoint)
        else:
            for endpoint in OPTIONS.items():
                cleanup_dates(endpoint)
        return

    if args.endpoint:
        endpoint = args.endpoint[0]
        OPTIONS[endpoint]()
    else:
        for func in OPTIONS.items():
            func()


if __name__ == "__main__":
    desc = "Copy data into django."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="qa_realtime",
        choices=list(OPTIONS.keys()),
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--cleanup", action="store_true",
        default=False, help="Cleanup"
    )

    args = inputparser.parse_args()

    engine = models.make_engine()
    session = models.set_session(engine)

    main()
