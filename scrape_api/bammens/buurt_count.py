import datetime
import db_helper
import argparse
import requests

from bammens.models import BuurtBewonerCounts


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


def main(args):
    store_bbga_buurten()


if __name__ == "__main__":
    desc = "Collect Buurt Inhabitants data from BBGA"
    inputparser = argparse.ArgumentParser(desc)
    args = inputparser.parse_args()
    engine = db_helper.make_engine()
    session = db_helper.set_session(engine)
    main(args)
    session.close()
