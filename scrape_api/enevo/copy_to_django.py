"""Copy raw data into django api models."""

import argparse
import logging
import db_helper


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
    CAST(data->>'site' as int) as site_id,
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

LINK_SITE = """
UPDATE enevo_enevocontainerslot
SET site_id = site_fk
WHERE site_fk IN (select id from enevo_enevosite)
"""

LINK_SITECONTENTTYPE = """
UPDATE enevo_enevocontainerslot
SET site_content_type_id = site_content_type_fk
WHERE site_content_type_fk IN (select id from enevo_enevositecontenttype)
"""

VALIDATE_CONTAINERS = """
UPDATE enevo_enevocontainer
SET valid = TRUE
WHERE customer_key IN (
select id_number from afvalcontainers_container
)
"""

INVALIDATE_CONTAINERS = """
UPDATE enevo_enevocontainer
SET valid = FALSE
WHERE customer_key NOT IN (
select id_number from afvalcontainers_container
)
"""


def link_container_slots():
    sql = LINK_SITE
    session.execute(sql)
    session.commit()

    sql = LINK_SITECONTENTTYPE
    session.execute(sql)
    session.commit()


def validate_containers():
    sql = VALIDATE_CONTAINERS
    session.execute(sql)
    session.commit()

    sql = INVALIDATE_CONTAINERS
    session.execute(sql)
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
    if args.link_container_slots:
        link_container_slots()
        return

    if args.validate_containers:
        validate_containers()
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
        "--link_container_slots", action="store_true",
        default=False, help="Link containerslots with sites and sitecontenttypes"
    )

    inputparser.add_argument(
        "--validate_containers", action="store_true",
        default=False, help="Validate the customer_keys are in bammens"
    )

    args = inputparser.parse_args()

    engine = db_helper.make_engine()
    session = db_helper.set_session(engine)

    main()

    session.close()
