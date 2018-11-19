import logging
import argparse
import asyncio

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence

# from aiopg.sa import create_engine as aiopg_engine
import db_helper

# logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Base = declarative_base()


async def main(args):
    """Main."""
    engine = db_helper.make_engine(section="dev")

    if args.drop:
        # resets everything
        LOG.warning("DROPPING ALL DEFINED TABLES")
        Base.metadata.drop_all(engine)

    LOG.warning("CREATING DEFINED TABLES")
    # recreate tables
    Base.metadata.create_all(engine)


class EnevoAlert(Base):
    """Raw Enevo container data."""
    __tablename__ = f"enevo_alert_raw"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


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


class EnevoFillLevel(Base):
    """Raw Enevo FillLevel data."""
    __tablename__ = f"enevo_filllevel"
    id = Column(Integer, Sequence("grl_seq"), primary_key=True)
    time = Column(String, index=True)
    fill_level = Column(Integer, index=True)
    site = Column(Integer, index=True)
    site_name = Column(String, index=True)
    site_content_type = Column(Integer, index=True)
    confidence = Column(Integer, index=True)
    frozen = Column(Boolean, index=True)


if __name__ == "__main__":
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--drop", action="store_true", default=False, help="Drop existing"
    )

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
