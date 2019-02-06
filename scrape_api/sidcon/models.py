import logging
import argparse
import asyncio

from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from geoalchemy2 import Geometry
from settings import Base

# from aiopg.sa import create_engine as aiopg_engine
import db_helper
from settings import KILO_ENVIRONMENT_OVERRIDES

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


SIDCON_TABLES = [
    # should never be dropped
    # "sidcon_container_status_raw",
    "sidcon_container_states",
]


async def create_tables(args):
    """Main."""
    engine = db_helper.make_engine(environment=KILO_ENVIRONMENT_OVERRIDES)

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in SIDCON_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)
    db_helper.alembic_migrate(engine)


class SidconRaw(Base):
    """Raw sidcon API data."""

    __tablename__ = f"sidcon_container_status_raw"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class SidconFillLevel(Base):
    """Sidcon Fill level Statusses.

    extracted from the json
    """

    __tablename__ = f"sidcon_container_states"
    __table_args__ = {'extend_existing': True}

    id = Column(
        Integer,
        Sequence('sidcon_container_states_sequence'),
        primary_key=True)  # Seq

    scraped_at = Column(TIMESTAMP, index=True)
    geometrie = Column(Geometry('POINT', srid=4326), index=True)
    valid = Column(Boolean)

    _id = Column(Integer, index=True)
    unit_id = Column(Integer, index=True)
    city = Column(String(100))
    number = Column(String(100))
    street = Column(String(150))

    filling = Column(Integer, index=True)   # "Filling": 2,
    device_id = Column(Integer)    # "DeviceId": 296,
    entity_id = Column(Integer)    # "EntityId": 1001,
    fraction = Column(String(50))  # "Fraction": "Rest Afval",
    status_id = Column(Integer)    # "StatusId": 285,
    limit_full = Column(Integer)   # "LimitFull": 100,
    # "Postalcode": null,
    container_id = Column(Integer, index=True)  # "ContainerId": 208,
    description = Column(String(50), index=True)   # "description": "RE K 00313",

    house_number = Column(Integer)   # house_number": "38",
    press_status = Column(Integer)   # "PressStatus": 3,
    press_current = Column(Integer)  # "PressCurrent": 32,

    status_device = Column(String(50))   # "StatusDevice": "NoError",
    container_name = Column(String(50))  # container name

    limit_near_full = Column(Integer)   # "LimitNearFull": 80,
    placement_date = Column(TIMESTAMP, index=True)
    # "PlacementDate": "2018-01-08T16:29:44Z",
    # "UserAddressId": null,
    battery_voltage = Column(Float)        # "batteryVoltage": 240.0,
    nr_press_strokes = Column(Integer)     # "NrPressStrokes": 5,
    drum_action_count = Column(Integer)    # "DrumActionCount": 7,
    network_strenght = Column(Integer)     # "NetworkStrength": 18,
    status_chip_cards = Column(String(50))  # "StatusChipcards": "Active",
    status_container = Column(String(100))  # "StatusContainer": "NoError",
    status_incidents = Column(Boolean)      # "StatusIncidents": false,
    max_nr_press_strokes = Column(Integer)  # "MaxNrPressStrokes": 0,
    status_trigger_name = Column(String(100))
    # "StatusTriggerName": "PressStopped"
    drum_position_status = Column(Integer)     # "DrumPositionStatus": 1,
    lock_position_status = Column(Integer)     # "LockPositionStatus": 2,
    nr_press_strokes_to_go = Column(Integer)    # "NrPressStrokesToGo": null,
    status_configuration = Column(String(50))
    # "StatusConfiguration": "Active",
    total_nr_press_strokes = Column(Integer)   # "TotalNrPressStrokes": 7936,
    total_nr_empty_detected = Column(Integer)  #
    communication_date_time = Column(TIMESTAMP, index=True)
    # "CommunicationDateTime": "2018-11-28T11:20:17.12Z",
    volume_correction_factor = Column(Float)
    # "VolumeCorrectionFactor": 1.0,
    max_dump_count_on_dump_location = Column(Integer)
    # "MaxDumpCountOnDumpLocation": 100,
    successfull_transaction_since_reset = Column(Integer)
    # "SuccessfulTransactionsSinceReset": 0,
    unsuccessfull_transaction_since_reset = Column(Integer)
    # "UnsuccessfulTransactionsSinceReset": null

    # DP manual added AKA site_id
    short_id = Column(Integer, index=True)  # short_id field

    # district = Column(String, index=True)
    # neighborhood = Column(String, index=True)
    # stadsdeel = Column(String(1), index=True)
    # buurt_code = Column(String(4), index=True)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables(args))
