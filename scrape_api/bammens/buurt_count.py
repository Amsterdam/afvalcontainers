import logging
import datetime
import db_helper
import argparse
import requests
from settings import KILO_ENVIRONMENT_OVERRIDES

from sqlalchemy.schema import Sequence
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

# Helper models to copy relevant data in.

Base = declarative_base()


class BuurtBewonerCounts(Base):
    """BBGA BEVOLKINGTOTAAL API data."""

    __tablename__ = f"buurt_counts"
    id = Column(Integer, Sequence("grl_seq_buurt"), primary_key=True)
    year = Column(Integer, index=True)
    buurt_code = Column(String(4), index=True)
    inhabitants = Column(Integer, index=True)


def reset_table(engine):
    # resets everything
    LOG.warning("RESTE buurt_count TABLES")
    Base.metadata.drop_all(engine)
    # recreate tables
    Base.metadata.create_all(engine)


def _store_raw_buurt_data(raw_response: dict):
    objects = []
    buurten = raw_response['results']
    # Store the location json!
    for item in buurten:
        grj = dict(
            year=int(item["jaar"]),
            buurt_code=item["gebiedcode15"],
            inhabitants=item["waarde"]
        )
        objects.append(grj)

    if objects:
        insert_stmt = BuurtBewonerCounts.__table__.insert()
        session.execute(insert_stmt, objects)
        session.commit()


def _get_bbga_bevolking(year):

    url = "https://api.data.amsterdam.nl/bbga/cijfers/"

    params = {
        'variabele': 'BEVTOTAAL',
        'jaar': year,
        'page_size': 1000,
    }

    r = requests.get(url, params=params)
    return r.json()


def store_bbga_buurten():
    session.execute('''TRUNCATE TABLE buurt_counts''')
    session.commit()
    start = datetime.datetime.now().year
    years = []
    for x in range(6):
        years.append(start - x)

    for year in years:
        raw_data = _get_bbga_bevolking(year)
        _store_raw_buurt_data(raw_data)


def main(args, engine, session):
    reset_table(engine)
    store_bbga_buurten()


if __name__ == "__main__":
    desc = "Collect Buurt Inhabitants data from BBGA"
    inputparser = argparse.ArgumentParser(desc)
    args = inputparser.parse_args()
    engine = db_helper.make_engine(environment=KILO_ENVIRONMENT_OVERRIDES)
    session = db_helper.set_session(engine)
    main(args, engine, session)
    session.close()
