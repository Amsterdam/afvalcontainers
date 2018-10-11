import os
import logging
from settings import config_auth

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database

from sqlalchemy.engine.url import URL

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

Session = sessionmaker()


def make_conf(section, environment_overrides=[]):
    """Create database connection."""
    db = {
        'host': config_auth.get(section, "host"),
        'port': config_auth.get(section, "port"),
        'database': config_auth.get(section, "dbname"),
        'username': config_auth.get(section, "user"),
        'password': config_auth.get(section, "password"),
    }

    # override defaults with environment settings
    for var, env in environment_overrides:
        if os.getenv(env):
            db[var] = os.getenv(env)

    CONF = URL(
        drivername="postgresql",
        username=db['username'],
        password=db['password'],
        host=db['host'],
        port=db['port'],
        database=db['database'],
    )

    host, port, name = db['host'], db['port'], db['database']
    LOG.info(f"Database config {host}:{port}:{name}")
    return CONF


def create_db(section="test", environment=[]):
    """Create the database."""
    CONF = make_conf(section)
    LOG.info(f"Created database")
    if not database_exists(CONF):
        create_database(CONF)


def drop_db(section="test", environment=[]):
    """Cleanup."""
    LOG.info(f"Drop database")
    CONF = make_conf(section)
    if database_exists(CONF):
        drop_database(CONF)


def make_engine(section="docker", environment=[]):
    CONF = make_conf(section)
    engine = create_engine(CONF)
    return engine


def set_session(engine):
    global session
    Session.configure(bind=engine)
    # create a configured "session" object for tests
    session = Session()
    return session
