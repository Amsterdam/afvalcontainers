"""ETL for converting raw enevo measurement to cleaned measurements.

We downloaded the raw source data with the slurp code. Now we have the original
data safe and sound.  This enables us to convert the raw data in usable data
records and merge usable information with it. And as a BONUS we can do it again
later in the future since the raw original data is safely stored.

TODO add datapunt site / enevo site information to the records
"""

import logging
import argparse
import datetime

import db_helper
from enevo import models

from settings import KILO_ENVIRONMENT_OVERRIDES

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


"""
{
    'site': 344792,
    'time': '2019-01-03T20:00:00Z',
    'frozen': False,
    'siteName': 'DE TOURTON BRUYNSSTRAAT 11 (PL F 30243)',
    'fillLevel': 41,
    'confidence': 100,
    'contentType': 1821,
    'containerSlot': 406148,
    'contentTypeName': 'PLASTIC ASW',
    'siteContentType': 538989,
    'containerSlotName': '1'
}
"""


def extract_one_raw_record(raw_record):

    rows = 0
    errors = 0
    time = None

    new_records = []

    for record in raw_record.data['fillLevels']:
        rows += 1
        new = dict(
            time=record['time'],
            frozen=record['frozen'],
            fill_level=record['fillLevel'],
            confidence=record['confidence'],
            container_slot=record.get('containerSlot'),
            content_type=record['contentType'],
            content_type_name=record['contentTypeName'],
            e_site_content_type=record['siteContentType'],
            e_site=record['site'],
            e_site_name=record['siteName'],
            container_slot_name=record.get('containerSlotName'),
        )

        new_records.append(new)

    if new_records:
        db_session = db_helper.session
        time = new_records[-1]['time']
        insert_stmt = models.EnevoFillLevel.__table__.insert()
        db_session.execute(insert_stmt, new_records)
        db_session.commit()

    log.debug('rows: %10d errors: %d %s', rows, errors, time)
    return rows, errors


def extract_measurements():
    """Extract Validate and Load the raw measurements.

    We continue were we left off by checking the time attribute.
    """
    db_session = db_helper.session
    measurements = models.EnevoFillLevel
    raw_measurements = models.EnevoFillLevelRaw

    # find date of latest cleaned measurement
    m = (
        db_session.query(measurements)
        .filter(measurements.time is not None)
        .order_by(measurements.time.desc())
        .first()
    )

    if m:
        left_off = m.time
    else:
        # default left_off time
        left_off = datetime.datetime(2014, 1, 1)

    # find all new raw measurements
    raw_new = (
        db_session.query(raw_measurements)
        .filter(raw_measurements.time is not None)
        .filter(raw_measurements.time > left_off)
        .order_by(raw_measurements.time.asc())
    )

    log.debug('New records found: %s since %s', raw_new.count(), left_off)

    total_records = 0
    total_errors = 0
    for raw_record in raw_new:
        total, errors = extract_one_raw_record(raw_record)
        total_records += total
        total_errors += errors

    log.debug("Total New %d, Total Errors %d", total_records, total_errors)


def main(make_engine=True):
    """Start ETL.

    When testing we can turn of endgine creation.
    """
    if make_engine:
        engine = db_helper.make_engine(
            section="docker",
            environment=KILO_ENVIRONMENT_OVERRIDES)
        db_helper.set_session(engine)

    extract_measurements()


if __name__ == "__main__":
    desc = "ETL Enevo API raw data"
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    main()
