import logging
import argparse
import asyncio

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from sqlalchemy import MetaData
from geoalchemy2 import Geometry  # noqa

import db_helper

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()

IMPORT_PREFIX = ''


async def main(args):
    """Table management."""
    engine = db_helper.make_engine(section="docker")
    session = db_helper.set_session(engine)

    if args.dropall:
        LOG.warning("DROPPING ALL DEFINED TABLES")
        # resets everything
        Base.metadata.drop_all(engine)

    if args.drop:
        # resets non raw tables
        LOG.warning("DROPPING ALL DROP TABLES")
        for table in DROP_TABLES:
            table = table.__table__.name
            session.execute(f"DROP table if exists {table};")
        session.commit()

    if args.live:
        LOG.warning("CREATING LIVE RELATED TABLES")
        meta = MetaData(engine)
        meta.reflect()

        for table in LIVE_TABLES:
            table_name = table.__table__.name
            if table_name not in meta.tables:
                table.meta.create()
        return

    LOG.warning("CREATING ALL DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class EnevoContainer(Base):
    """Raw Enevo container data."""

    __tablename__ = f"enevo_container_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoContainerType(Base):
    """Raw Enevo ContainerType data."""

    __tablename__ = f"enevo_containertype_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoContainerSlot(Base):
    """Raw Enevo ContainerSlot data."""

    __tablename__ = f"enevo_containerslot_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoContentType(Base):
    """Raw Enevo ContentType data."""

    __tablename__ = f"enevo_contenttype_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoSite(Base):
    """Raw Enevo Sites data."""

    __tablename__ = f"enevo_site_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoSiteContentType(Base):
    """Raw Enevo SiteContentType data."""

    __tablename__ = f"enevo_sitecontenttype_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoDevice(Base):
    """Raw Enevo Device data."""

    __tablename__ = f"enevo_device_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoServiceList(Base):
    """Raw Enevo ServiceList data."""

    __tablename__ = f"enevo_servicelist_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoServiceEvent(Base):
    """Raw Enevo ServiceEvent data."""

    __tablename__ = f"enevo_serviceevent_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoAlertRaw(Base):
    """Raw Enevo Alert data.

    with history
    """

    __tablename__ = f"enevo_alert_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    time = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoFillLevelRaw(Base):
    """Raw Enevo FillLevel data.

    with history.
    """

    __tablename__ = f"enevo_filllevel_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    time = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class EnevoFillLevel(Base):
    """Enevo FillLevel data. used in data."""

    __tablename__ = f"enevo_filllevel"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    time = Column(String, index=True)
    fill_level = Column(Integer, index=True)
    site = Column(Integer, index=True)
    site_name = Column(String, index=True)
    site_content_type = Column(Integer, index=True)
    confidence = Column(Integer, index=True)
    frozen = Column(Boolean, index=True)


DROP_TABLES = [
    EnevoFillLevel,
]


LIVE_TABLES = [
    EnevoFillLevel,
    EnevoFillLevelRaw,
    # EnevoAlert
    EnevoAlertRaw
]


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--dropall", action="store_true",
        default=False, help="Drop EVERYTHING WHATCH OUT!"
    )

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    inputparser.add_argument(
        "--live", action="store_true", default=False,
        help="create only live table data"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
