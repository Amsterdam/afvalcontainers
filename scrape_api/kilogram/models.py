import logging
import argparse
import asyncio

from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from geoalchemy2 import Geometry

# from aiopg.sa import create_engine as aiopg_engine
import db_helper
from settings import KILO_ENVIRONMENT_OVERRIDES

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()

KILOGRAM_TABLES = [
    "kilogram_weigh_raw",
    "kilogram_weigh_measurement",
]


async def create_tables(args):
    """Main."""
    engine = db_helper.make_engine(environment=KILO_ENVIRONMENT_OVERRIDES)

    session = db_helper.set_session(engine)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        for table in KILOGRAM_TABLES:
            session.execute(f"DROP table if exists {table};")
        session.commit()
        # Base.metadata.drop_all(engine)

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class KilogramRaw(Base):
    """Raw kilogram.nl API data."""

    __tablename__ = f"kilogram_weigh_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    system_id = Column(Integer, index=True)
    weigh_at = Column(TIMESTAMP, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class KilogramMeasurement(Base):
    """Measurements.

    extracted from the json
    """

    __tablename__ = f"kilogram_weigh_measurement"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)  # Seq
    seq_id = Column(Integer, index=True)
    system_id = Column(Integer, index=True)
    weigh_at = Column(TIMESTAMP, index=True)
    container_ids = Column(String, index=True)
    container_count = Column(String, index=True)
    fill_chance = Column(Float)
    fill_level = Column(Float)
    fractie = Column(String, index=True)  # Afvalnaam
    first_weight = Column(Integer, index=True)
    second_weight = Column(Integer, index=True)
    net_weight = Column(Integer, index=True)
    district = Column(String, index=True)
    neighborhood = Column(String, index=True)
    stadsdeel = Column(String(1), index=True)
    buurt_code = Column(String(4), index=True)
    location = Column(String, index=True)
    site_id = Column(Integer, index=True)
    geometrie = Column(Geometry('POINT', srid=4326), index=True)
    valid = Column(Boolean, index=True)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables(args))
