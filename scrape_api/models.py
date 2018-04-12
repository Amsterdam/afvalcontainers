import logging
import argparse
import asyncio

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from sqlalchemy import create_engine
# from aiopg.sa import create_engine as aiopg_engine
from sqlalchemy.engine.url import URL

from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database

from settings import config_auth


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

Base = declarative_base()

Session = sessionmaker()

session = []


def make_conf(section):

    host = config_auth.get(section, 'host')
    port = config_auth.get(section, 'port')
    db = config_auth.get(section, 'dbname')

    CONF = URL(
        drivername='postgresql',
        username=config_auth.get(section, 'user'),
        password=config_auth.get(section, 'password'),
        host=host,
        port=port,
        database=db,
    )

    log.info(f"Database config {host}:{port}:{db}")
    return CONF


def create_db(section='test'):
    CONF = make_conf(section)
    log.info(f"Created database")
    if not database_exists(CONF):
        create_database(CONF)


def drop_db(section='test'):
    log.info(f"Drop database")
    CONF = make_conf(section)
    if database_exists(CONF):
        drop_database(CONF)


def make_engine(section='docker'):
    CONF = make_conf(section)
    engine = create_engine(CONF)
    return engine


def set_engine(engine):
    global session
    Session.configure(bind=engine)
    # create a configured "session" object for tests
    session = Session()
    return session


class Container(Base):
    """
    Raw json containers
    """
    __tablename__ = f'bammens_container_raw'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class Well(Base):
    """
    Raw json location of wells
    """
    __tablename__ = f'bammens_well_raw'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


class ContainerType(Base):
    """
    Raw json proxy for api.
    """
    __tablename__ = f'bammens_containertype_raw'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    scraped_at = Column(TIMESTAMP, index=True)
    data = Column(JSONB)


async def main(args):
    """Main
    """
    engine = make_engine()

    if args.drop:
        # resets everything
        log.warning('DROPPING ALL DEFINED TABLES')
        Base.metadata.drop_all(engine)

    log.warning('CREATING DEFINED TABLES')
    # recreate tables
    Base.metadata.create_all(engine)
    # create tables


if __name__ == '__main__':
    desc = "Create/Drop defined model tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        '--drop',
        action='store_true',
        default=False,
        help="Drop existing")

    args = inputparser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
