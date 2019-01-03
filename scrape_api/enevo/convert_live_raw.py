"""ETL for converting raw enevo measurement to cleaned measurements.

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


def extract_one_raw_record(raw_record):
    print(raw_record)


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
        left_off = datetime.datetime(2014, 0, 0)

    # find all new raw measurements
    raw_new = (
        db_session.query(raw_measurements)
        .filter(raw_measurements.time is not None)
        .filter(raw_measurements.time > left_off)
        .order_by(raw_measurements.time.desc())
        .limit(100)
    )

    for raw_record in raw_new:
        extract_one_raw_record(raw_record)


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
