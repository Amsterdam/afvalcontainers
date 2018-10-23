import argparse
import logging
from sqlalchemy.sql import select

from settings import KILO_ENVIRONMENT_OVERRIDES
from kilogram import models
import datetime
import db_helper

from types import SimpleNamespace
# from sqlalchemy import bindparam

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def clean():
    session = db_helper.session
    session.execute('''TRUNCATE TABLE kilogram_weigh_measurement''')
    session.commit()


def validate_date(measurement, idx):
    """Validate every measurement."""
    # create a date time
    date = measurement[idx.date]
    time = measurement[idx.time]

    if date and time:
        weigh_at = datetime.datetime.strptime(
            f'{date} {time}', '%Y-%m-%d %H:%M:%S')
    else:
        LOG.warning('DATE %s', measurement)
        weigh_at = None

    return weigh_at


def validate_geo(measurement, idx):
    """Validate geo, if not ok return 0, 0."""
    try:
        lon = float(measurement[idx.lon])
        lat = float(measurement[idx.lat])
    except ValueError:
        lon, lat = 0, 0
        LOG.debug('LON LAT ERRROR %s', measurement)
    # when unknown we default to 0,0
    if lon and lat:
        geometrie = f"SRID=4326;POINT({lon} {lat})"
    else:
        geometrie = None  # f"SRID=4326;POINT(0 0)"

    return geometrie


def validate_weight(measurement, idx):
    """Validate the weights."""
    try:
        net_weight = int(measurement[idx.net_weight])
    except ValueError:
        net_weight = None

    try:
        first_weight = int(measurement[idx.first_weight])
    except ValueError:
        first_weight = None

    try:
        second_weight = int(measurement[idx.second_weight])
    except ValueError:
        second_weight = None

    return first_weight, second_weight, net_weight


def validate_float(measurement, idx):
    """Validate the expected float values."""
    fill_level = None
    fill_chance = None

    if idx.fill_level:
        try:
            fill_level = float(measurement[idx.fill_level])
        except ValueError:
            pass

    if idx.fill_chance:
        try:
            fill_chance = float(measurement[idx.fill_chance])
        except ValueError:
            fill_chance = None

    return fill_chance, fill_level


def validate_extra(measurement, idx):
    """Validate some extra fields."""
    fractie = 'Rest'
    location = None,
    site_id = None

    if idx.site_id:
        try:
            site_id = int(measurement[idx.site_id])
        except ValueError:
            pass

    if idx.fractie:
        fractie = measurement[idx.fractie]

    if idx.location:
        try:
            location = int(measurement[idx.location])
        except ValueError:
            pass

    return fractie, location, site_id


"""
Expected fields with example data

"Fields": [
    "SystemId",       "5",
    "Seq",            "9290",
    "Date",           "2018-10-01",
    "Time",           "09:17:54",
    "NoOfCont",       "1",
    "ContIds",        "74006",
    "TotalVolume",    "4",
    "Location",       "Opijnenhof 106",  # skipped!
    "District",       "Zuid Oost",
    "Neighborhood",   "Reigersbos Noord",
    "FractionId",    "Rest",
    "FirstWeight",   "1070",
    "SecondWeight",  "835",
    "NettWeight",    "235",
    "Latitude",      "52.29538",
    "Longitude"      "4.96802",
]

"""


possible_missing = (
    # Source, target, default
    ('FillLevel', 'fill_level', None),
    ('FillChance', 'fill_chance', None),
    ('FractionId', 'fractie', 'Rest'),
    ('Location', 'location', None),
)


def make_field_mapping(fields, system_id):
    """Map fields to index map."""
    idx = dict(
        system_id=fields.index("SystemId"),
        _id=fields.index('Seq'),
        date=fields.index('Date'),
        time=fields.index('Time'),
        site_id=fields.index('CustId'),
        district=fields.index('District'),
        container_ids=fields.index('ContIds'),
        container_count=fields.index('NoOfCont'),
        volume=fields.index('TotalVolume'),
        neighborhood=fields.index('Neighborhood'),
        first_weight=fields.index("FirstWeight"),
        second_weight=fields.index("SecondWeight"),
        net_weight=fields.index("NettWeight"),
        lat=fields.index("Latitude"),
        lon=fields.index("Longitude")
    )

    for source, target, default in possible_missing:
        if source in fields:
            idx[target] = fields.index(source)
        else:
            idx[target] = default

    return SimpleNamespace(**idx)


def extract_one_resultset(fields, records, system_id=None):
    """Extract api response to measurement records."""
    errors = 0
    rows = 0
    session = db_helper.session
    extracted = []

    idx = make_field_mapping(fields, system_id)
    if not idx:
        errors += len(records)
        return errors, errors

    for measurement in records:
        rows += 1
        weigh_at = validate_date(measurement, idx)

        # skip record if there is no time
        if not weigh_at:
            errors += 1
            continue

        geometrie = validate_geo(measurement, idx)

        first_weight, second_weight, net_weight = \
            validate_weight(measurement, idx)
        fill_chance, fill_level = validate_float(measurement, idx)
        fractie, location, site_id = validate_extra(measurement, idx)

        if not second_weight or first_weight or net_weight:
            # we store it to be able to keep track
            # of progress
            errors += 1

        new = {
            'seq_id': measurement[idx._id],
            'weigh_at': weigh_at,
            'system_id': measurement[idx.system_id],
            'container_ids': measurement[idx.container_ids],
            'container_count': measurement[idx.container_count],
            'fractie': fractie,
            'first_weight': first_weight,
            'fill_level': fill_level,
            'fill_chance': fill_chance,
            'second_weight': second_weight,
            'net_weight': net_weight,
            'district': measurement[idx.district],
            'neighborhood': measurement[idx.neighborhood],
            'location': location,
            'site_id': site_id,
            'geometrie': geometrie
        }

        extracted.append(new)

    if extracted:
        insert_stmt = models.KilogramMeasurement.__table__.insert()
        session.execute(insert_stmt, extracted)
        session.commit()

    return rows, errors


def extract_measurements():
    session = db_helper.session
    measurements = models.KilogramMeasurement
    api_source = models.KilogramRaw
    s = select([api_source])
    results = session.execute(s)
    rows = 0
    errors = 0

    # session.execute('''TRUNCATE TABLE kilogram_weigh_measurement''')
    # session.commit()

    for row in results:
        api_data = row[4]
        system_id = row[1]
        fields = api_data['Fields']
        records = api_data['Records']

        # find date of latest measurement
        m = (
            session.query(measurements)
            .filter(measurements.system_id == system_id)
            .filter(measurements.weigh_at is not None)
            .order_by(measurements.weigh_at.desc())
            .first()
        )

        if m and m.weigh_at >= row.weigh_at:
            LOG.debug('skipping %s %s', m.system_id, m.weigh_at)
            continue

        LOG.info(row.id)
        LOG.info(row.weigh_at)
        # new measurements found!
        row_new, error_new = extract_one_resultset(
            fields, records, system_id=system_id)
        rows += row_new
        errors += error_new

    LOG.info('RECORDS %s ERRORS %s', rows, errors)

    if errors > 50000:
        raise ValueError("Something went wrong. API fields changed?")


UPDATE_BUURT = """
UPDATE {target_table} tt
SET buurt_code = b.vollcode
FROM (SELECT * from buurt_simple) as b
WHERE ST_DWithin(b.wkb_geometry, tt.geometrie, 0)
AND buurt_code is null
AND tt.geometrie IS NOT NULL
"""

UPDATE_STADSDEEL = """
UPDATE {target_table} tt
SET stadsdeel = s.code
FROM (SELECT * from stadsdeel) as s
WHERE ST_DWithin(s.wkb_geometry, tt.geometrie, 0)
AND stadsdeel IS NULL
AND tt.geometrie IS NOT NULL
"""


def link_gebieden():
    target_table = 'kilogram_weigh_measurement'
    u_sql = UPDATE_STADSDEEL.format(target_table=target_table)
    session.execute(u_sql)
    session.commit()

    target_table = 'kilogram_weigh_measurement'
    u_sql = UPDATE_BUURT.format(target_table=target_table)
    session.execute(u_sql)
    session.commit()


def main():
    if args.link_gebieden:
        link_gebieden()
        return
    if args.cleanup:
        clean()
    if args.geoview:
        # create_container_view()
        return
    if args.link_containers:
        # link_containers_to_wells()
        return

    extract_measurements()


def get_session():
    engine = db_helper.make_engine(environment=KILO_ENVIRONMENT_OVERRIDES)
    session = db_helper.set_session(engine)
    return engine, session


if __name__ == "__main__":
    desc = "Copy data into django."
    inputparser = argparse.ArgumentParser(desc)

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
        "--link_containers", action="store_true",
        default=False, help="Cleanup"
    )

    args = inputparser.parse_args()
    engine, session = get_session()
    # conn = engine.connect()
    main()
    session.close()
