"""Copy raw data into django api models."""

import argparse
from enevo import models
import logging
from sqlalchemy.sql import select
from sqlalchemy import bindparam
import db_helper

from bammens.validation import validate_counts
from bammens.validation import validate_attribute_counts


log = logging.getLogger(__name__)

INSERT_CONTENTTYPES = """
INSERT INTO enevo_enevocontenttype (
    id,
    category,
    category_name,
    name,
    state,
    weight_to_volume_ratio,
    last_modified
)
SELECT
    id,
    CAST(data->>'category' as int) as category,
    CAST(data->>'categoryName' as varchar) as category_name,
    CAST(data->>'name' as varchar) as name,
    CAST(data->>'state' as varchar) as state,
    CAST(data->>'weightToVolumeRatio' as float) as weight_to_volume_ration,
    CAST(data->>'lastModified' as timestamp) as last_modified
FROM
    enevo_contenttype_raw;
"""  # noqa

INSERT_SITES = """
INSERT INTO enevo_enevosite (
    id,
    type,
    name,
    area,
    address,
    city,
    country,
    postal_code,
    geometrie,
    geometrie_rd,
    photo,
    last_modified
)
SELECT
    id,
    CAST(data->>'type' as int) as type,
    CAST(data->>'name' as varchar) as name,
    CAST(data->>'area' as int) as area,
    CAST(data->>'address' as varchar) as address,
    CAST(data->>'city' as varchar) as city,
    CAST(data->>'country' as varchar) as country,
    CAST(data->>'postalCode' as varchar) as postal_code,
    ST_SetSRID(
        ST_POINT(
            CAST(data->>'longitude' as float),
            CAST(data->>'latitude' as float)
        ), 4326) as geometrie,
    ST_Transform(
        ST_SetSRID(
            ST_POINT(
                CAST(data->>'longitude' as float),
                CAST(data->>'latitude' as float)
            ), 4326), 28992) as geometrie,
    CAST(data->>'photo' as bool) as photo,
    CAST(data->>'lastModified' as timestamp) as last_modified
FROM
    enevo_site_raw;
"""  # noqa


INSERT_SITECONTENTTYPES = """
INSERT INTO enevo_enevositecontenttype (
    id,
    content_type_id,
    content_type_name,
    category_name,
    site_id,
    fill_level,
    date_when_full,
    build_up_rate,
    fill_up_time,
    last_service_event,
    last_modified
)
SELECT
    id,
    CAST(data->>'contentType' as int) as content_type_id,
    CAST(data->>'contentTypeName' as varchar) as content_type_name,
    CAST(data->>'categoryName' as varchar) as category_name,
    CAST(data->>'site_id' as int) as site,
    CAST(data->>'fillLevel' as int) as fill_level,
    CAST(data->>'dateWhenFull' as timestamp) as date_when_full,
    CAST(data->>'buildUpRate' as float) as build_up_rate,
    CAST(data->>'fillUpTime' as int) as fill_up_time,
    CAST(data->>'lastServiceEvent' as timestamp) as last_service_event,
    CAST(data->>'lastModified' as timestamp) as last_modified
FROM
    enevo_sitecontenttype_raw;
"""  # noqa

INSERT_CONTAINERTYPES = """
INSERT INTO enevo_enevocontainertype (
    id,
    name,
    volume,
    sensor_height,
    full_height,
    shape,
    has_bag,
    servicing_amount,
    servicing_method,
    last_modified
)
SELECT
    id,
    CAST(data->>'name' as varchar) as name,
    CAST(data->>'volume' as int) as volume,
    CAST(data->>'sensorHeight' as float) as sensor_height,
    CAST(data->>'fullHeight' as float) as full_height,
    CAST(data->>'shape' as varchar) as shape,
    CAST(data->>'hasBag' as bool) as has_bag,
    CAST(data->>'servicingAmount' as varchar) as servicing_amount,
    CAST(data->>'servicingMethod' as varchar) as servicing_method,
    CAST(data->>'lastModified' as timestamp) as last_modified
FROM
    enevo_containertype_raw;
"""  # noqa

INSERT_CONTAINERSLOTS = """
INSERT INTO enevo_enevocontainerslot (
    id,
    name,
    content_type_id,
    container,
    site_content_type_fk,
    site_fk,
    fill_level,
    date_when_full,
    last_service_event,
    photo,
    last_modified
)
SELECT
    id,
    CAST(data->>'name' as varchar) as name,
    CAST(data->>'contentType' as int) as content_type_id,
    CAST(data->>'container' as int) as container,
    CAST(data->>'siteContentType' as int) as site_content_type_fk,
    CAST(data->>'site' as int) as site_fk,
    CAST(data->>'fillLevel' as int) as fill_level,
    CAST(data->>'dateWhenFull' as timestamp) as date_when_full,
    CAST(data->>'lastServiceEvent' as timestamp) as last_service_event,
    CAST(data->>'photo' as bool) as photo,
    CAST(data->>'lastModified' as timestamp) as last_modified
FROM
    enevo_containerslot_raw;

"""  # noqa


INSERT_CONTAINERS = """
INSERT INTO enevo_enevocontainer (
    id,
    container_type_id,
    site_id,
    site_content_type_id,
    container_slot_id,
    customer_key,
    geometrie,
    geometrie_rd,
    geo_accuracy,
    last_modified
)
SELECT
    id,
    CAST(data->>'type' as int) as container_type_id,
    CAST(data->>'site' as int) as site_id,
    CAST(data->>'siteContentType' as int) as site_content_type_id,
    CAST(data->>'containerSlot' as int) as container_slot_id,
    CAST(data->>'customerKey' as varchar) as customer_key,
    ST_SetSRID(
        ST_POINT(
            CAST(data->'cellLocation'->>'longitude' as float),
            CAST(data->'cellLocation'->>'latitude' as float)
        ), 4326) as geometrie,
    ST_Transform(
        ST_SetSRID(
            ST_POINT(
                CAST(data->'cellLocation'->>'longitude' as float),
                CAST(data->'cellLocation'->>'latitude' as float)
            ), 4326), 28992) as geometrie,
    CAST(data->'cellLocation'->>'accuracy' as int) as geo_accuracy,
    CAST(data->>'lastModified' as timestamp) as last_modified

FROM
    enevo_container_raw;
"""  # noqa


INSERT_ALERTS = """
INSERT INTO enevo_enevoalert (
    id,
    type,
    type_name,
    reported,
    last_observed,
    site_id,
    site_name,
    area,
    area_name,
    content_type_id,
    content_type_name,
    start
)
SELECT
    id,
    CAST(data->>'type' as int) as type,
    CAST(data->>'typeName' as varchar) as type_name,
    CAST(data->>'reported' as timestamp) as reported,
    CAST(data->>'lastObserved' as timestamp) as last_observed,
    CAST(data->>'site' as int) as site,
    CAST(data->>'site_name' as varchar) as site_name,
    CAST(data->>'area' as int) as area,
    CAST(data->>'areaName' as varchar) as area_name,
    CAST(data->>'contentType' as int) as content_type_id,
    CAST(data->>'contentTypeName' as varchar) as content_type_name,
    CAST(data->>'start' as timestamp) as start
FROM
    enevo_alert_raw;
"""  # noqa


def update_contenttypes():
    sql = INSERT_CONTENTTYPES
    session.execute("TRUNCATE TABLE enevo_enevocontenttype CASCADE;")
    session.execute(sql)
    session.commit()


def update_containertypes():
    sql = INSERT_CONTAINERTYPES
    session.execute("TRUNCATE TABLE enevo_enevocontainertype CASCADE;")
    session.execute(sql)
    session.commit()


def update_sites():
    sql = INSERT_SITES
    session.execute("TRUNCATE TABLE enevo_enevosite CASCADE;")
    session.execute(sql)
    session.commit()


def update_sitecontenttypes():
    sql = INSERT_SITECONTENTTYPES
    session.execute("TRUNCATE TABLE enevo_enevositecontenttype CASCADE;")
    session.execute(sql)
    session.commit()


def update_containers():
    sql = INSERT_CONTAINERS
    session.execute("TRUNCATE TABLE enevo_enevocontainer CASCADE;")
    session.execute(sql)
    session.commit()


def update_containerslots():
    sql = INSERT_CONTAINERSLOTS
    session.execute("TRUNCATE TABLE enevo_enevocontainerslot CASCADE;")
    session.execute(sql)
    session.commit()


def update_alerts():
    sql = INSERT_ALERTS
    session.execute("TRUNCATE TABLE enevo_enevoalert CASCADE;")
    session.execute(sql)
    session.commit()


def validate_timestamps(item):
    """Clean up invalid timestamps."""
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
    """Bad dates needs to be cleaned up."""
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


LINK_SQL = """
UPDATE afvalcontainers_container bc
SET well_id = wlist.id
FROM (
    SELECT ww.id, ww.cid::int from  (
        SELECT w.id, jsonb_array_elements_text(w.containers_bron) AS cid
        FROM afvalcontainers_well w) as  ww) as wlist
WHERE wlist.cid = bc.id
"""

UPDATE_BUURT = """
UPDATE {target_table} tt
SET buurt_code = b.vollcode
FROM (SELECT * from buurt_simple) as b
WHERE ST_DWithin(b.wkb_geometry, tt.geometrie_rd, 0)
"""

UPDATE_STADSDEEL = """
UPDATE {target_table} tt
SET stadsdeel = s.code
FROM (SELECT * from stadsdeel) as s
WHERE ST_DWithin(s.wkb_geometry, tt.geometrie_rd, 0)
"""


def link_containers_to_wells():
    sql = LINK_SQL
    session.execute(sql)
    session.commit()


def link_gebieden():
    target_table = 'afvalcontainers_well'
    u_sql = UPDATE_STADSDEEL.format(target_table=target_table)
    session.execute(u_sql)
    session.commit()

    target_table = 'afvalcontainers_well'
    u_sql = UPDATE_BUURT.format(target_table=target_table)
    session.execute(u_sql)
    session.commit()


OPTIONS = {
    "container_types": update_containertypes,
    "sites": update_sites,
    "site_content_types": update_sitecontenttypes,
    "container_slots": update_containerslots,
    "containers": update_containers,
    "alerts": update_alerts,
    "content_types": update_contenttypes,
}

TABLE_COUNTS = [
    ('afvalcontainers_well', 12000),
    ('afvalcontainers_container', 12000),
    ('afvalcontainers_containertype', 200),
    ('container_locations', 12000),
]

VALIDATE_SQL = [
    ("""select count(*) from afvalcontainers_well
        where stadsdeel is null""", 0, 5),
    ("""select count(*) from afvalcontainers_well
        where buurt_code is null""", 0, 5),

    ("""select count(*) from afvalcontainers_well
        where extra_attributes->'missing_bgt_afval' = 'true'""",
        0, 5000)
]


def main():  # noqa
    if args.link_gebieden:
        link_gebieden()
        return
    if args.validate:
        validate_counts(TABLE_COUNTS, session)
        validate_attribute_counts(VALIDATE_SQL, session)
        return
    if args.link_containers:
        link_containers_to_wells()
        return
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
        default="",
        choices=list(OPTIONS.keys()),
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--link_gebieden", action="store_true",
        default=False, help="Voeg stadsdeel / buurt to aan datasets"
    )

    inputparser.add_argument(
        "--validate", action="store_true",
        default=False, help="Validate counts to check import was OK"
    )

    inputparser.add_argument(
        "--geoview", action="store_true",
        default=False, help="Geoview containers"
    )

    inputparser.add_argument(
        "--cleanup", action="store_true",
        default=False, help="Cleanup"
    )

    inputparser.add_argument(
        "--wastename", action="store_true",
        default=False, help="Add waste name to containers"
    )

    inputparser.add_argument(
        "--link_containers", action="store_true",
        default=False, help="Cleanup"
    )

    args = inputparser.parse_args()

    engine = db_helper.make_engine("dev")
    session = db_helper.set_session(engine)

    main()

    session.close()
