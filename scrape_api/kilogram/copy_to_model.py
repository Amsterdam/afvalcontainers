
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
        geometrie = f"SRID=4326;POINT(0 0)"

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


def validate_extra(measurement, idx):
    """Validate some extra fields."""
    fractie = 'Rest'

    if idx.afval_naam:
        fractie = measurement[idx.afval_naam]

    try:
        location_id = int(measurement[idx.location])
    except ValueError:
        location_id = None,

    return fractie, location_id


def make_field_mapping(fields, system_id):
    """Map fields to index map."""
    idx = dict(
        _id=fields.index('Seq'),
        date=fields.index('Date'),
        time=fields.index('Time'),
        container=fields.index('ContNr'),
        first_weight=fields.index("FirstWeight"),
        second_weight=fields.index("SecondWeight"),
        net_weight=fields.index("NettWeight"),
        system_id=fields.index("SystemId"),
        location=fields.index("LocationId"),
        lat=fields.index("Latitude"),
        lon=fields.index("Longitude")
    )

    if 'AfvalNaam' in fields:
        idx['afval_naam'] = fields.index('AfvalNaam')
    else:
        idx['afval_naam'] = None
        LOG.warning('FIELD MAPPING %s', fields)
        LOG.warning('Systemid %s', system_id)
        return

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
        fractie, location_id = validate_extra(measurement, idx)

        if not second_weight or first_weight or net_weight:
            # we store it to be able to keep track
            # of progress
            errors += 1

        new = {
            'seq_id': measurement[idx._id],
            'weigh_at': weigh_at,
            'system_id': measurement[idx.system_id],
            'location_id': location_id,
            'container_id': measurement[idx.container],
            'fractie': fractie,
            'first_weight': first_weight,
            'second_weight': second_weight,
            'net_weight': net_weight,
            'geometrie': geometrie
        }

        if geometrie is None:
            new.pop('geometrie')

        extracted.append(new)

    if extracted:
        insert_stmt = models.KilogramMeasurement.__table__.insert()
        session.execute(insert_stmt, extracted)

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


def main():
    if args.link_gebieden:
        # link_gebieden()
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
