import logging
import argparse
import asyncio

from sqlalchemy import Column, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
# from geoalchemy2 import Geometry

# from aiopg.sa import create_engine as aiopg_engine
import db_helper

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()

EENVIRONMENT_OVERRIDES = [
    ('host', 'KILOGRAM_DB'),
    ('port', 'KILOGRAM_DB_PORT'),
    ('database', 'KILOGRAM_DB_NAME'),
    ('username', 'KILOGRAM_DB_USER'),
    ('password', 'KILOGRAM_DB_PASSWORD'),
]


async def main(args):
    """Main."""
    engine = db_helper.make_engine(environment=EENVIRONMENT_OVERRIDES)

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        Base.metadata.drop_all(engine)

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class KilogramRaw(Base):
    """Raw json containers."""

    __tablename__ = f"kilogram_weigh_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    system_id = Column(Integer, index=True)
    weigh_at = Column(TIMESTAMP, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
