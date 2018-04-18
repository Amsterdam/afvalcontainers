"""
Copy raw data into django api models
"""

import argparse
import models


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


# session.commit()


def update_containers():
    sql = INSERT_CONTAINERS
    session.execute("TRUNCATE TABLE afvalcontainers_container;")
    session.execute(sql)


def update_wells():
    insert = INSERT_WELLS
    session.execute("TRUNCATE TABLE afvalcontainers_well")
    session.execute(insert)


# session.commit()


OPTIONS = {
    "types": update_types, "containers": update_containers, "wells": update_wells
}


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

    args = inputparser.parse_args()

    session = models.make_engine()

    if args.endpoint:
        endpoint = args.endpoint[0]
        OPTIONS[endpoint]()
    else:
        for func in OPTIONS.items():
            func()
