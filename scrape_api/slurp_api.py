"""
save external API sources
"""

import aiohttp
# import aiopg
from aiohttp import ClientSession
import asyncio

import datetime
import os
import models
import logging
import argparse
import settings
import os.path

from dateutil import parser

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.ERROR)

ENVIRONMENT = os.getenv('ENVIRONMENT', 'acceptance')

WORKERS = 5

STATUS = {
    'done': False
}

URL_QUEUE = asyncio.Queue()
RESULT_QUEUE = asyncio.Queue()

ENDPOINTS = [
    'containertypes',
    'containers',
    'wells'
]

ENDPOINT_MODEL = {
    'containertypes': models.ContainerTypes,
    'containers': models.Containers,
    'wells': models.Well
}

ENDPOINT_URL = {
    'containertypes': '{host}:{port}/gemeenteamsterdam/realtime/timerange',
    'wells': '{host}:{port}/gemeenteamsterdam/expected/timerange',
    'containers': '{host}:{port}/gemeenteamsterdam/realtime/current',
}


api_config = {
    'password': os.getenv('QUANTILLION_PASSWORD'),
    'hosts': {
        'production': 'http://apis.quantillion.io',
        'acceptance': 'http://apis.quantillion.io',
        # 'acceptance': 'http://apis.development.quantillion.io',
    },
    'port': 3001,
    'username': 'gemeenteAmsterdam',
}


AUTH = (api_config['username'], api_config.get('password'))


async def fetch(url, session, params=None, auth=None):
    async with session.get(url) as response:
        return await response


async def get_the_json(session, endpoint) -> list:
    """
    Get some json of endpoint!
    """
    json = []
    params = {}
    response = None
    url = ENDPOINT_URL[endpoint]
    response = await fetch(url, params=params, auth=AUTH)

    if response is None:
        log.error('RESPONSE NONE %s %s', url, params)
        return []
    elif response.status_code == 200:
        log.debug(f' OK  {response.status_code}:{url}')
    elif response.status_code == 401:
        log.error(f' AUTH {response.status_code}:{url}')
    elif response.status_code == 500:
        log.debug(f'FAIL {response.status_code}:{url}')

    # we did WRONG requests. crash hard!
    elif response.status_code == 400:
        log.error(f' 400 {response.status_code}:{url}')
        raise ValueError('400. wrong request.')
    elif response.status_code == 404:
        log.error(f' 404 {response.status_code}:{url}')
        raise ValueError('404. NOT FOUND wrong request.')

    if response:
        json = response.json()

    return json


def add_locations_to_db(endpoint, json: list):
    """
    Given json api response, store data in database
    """

    if not json:
        log.error('No data recieved')
        return

    db_model = ENDPOINT_MODEL[endpoint]

    # make new session
    session = models.Session()

    log.debug(f"Storing {len(json)} locations")

    # Store the location json!
    for loc in json:

        place_id = loc['place_id']
        scraped_at = parser.parse(loc['ScrapeTime'])

        grj = db_model(
            place_id=place_id,
            scraped_at=scraped_at,
            name=loc['name'],
            data=loc,
        )

        session.add(grj)

    session.commit()

    log.debug(f"Updated {len(json)} locations")


def delete_duplicates(db_model):
    """
    Remove duplacates from table.
    """
    # make new session
    session = models.Session()

    if session.query(db_model).count() == 0:
        raise ValueError('NO DATA RECIEVED WHATSOEVER!')

    log.debug('Count before %d', session.query(db_model).count())

    tablename = db_model.__table__.name
    session.execute(f"""
DELETE FROM {tablename} a USING (
     SELECT MIN(ctid) AS ctid, place_id, scraped_at
        FROM {tablename}
        GROUP BY (scraped_at, place_id) HAVING COUNT(*) > 1
 ) dups
 WHERE a.place_id = dups.place_id
 AND a.scraped_at = dups.scraped_at
 AND a.ctid <> dups.ctid
    """)
    session.commit()

    log.debug('Count after %d', session.query(db_model).count())


def get_previous_days():

    now = datetime.datetime.now()

    day = datetime.timedelta(days=1)

    today = now.date()
    tomorrow = (now + day).date()

    yield (str(today), str(tomorrow))

    # lets go 50 days in the past
    for i in range(1, settings.DAYS):
        past_time = now - i * day
        past_date1 = past_time.date()
        past_date2 = (past_time + day).date()
        yield (str(past_date1), str(past_date2))


async def do_request(work_id, session, endpoint, params={}):
    """
    Do batch request of LIMIT each
    """

    while True:
        log.debug('%d %s', work_id, params)
        url = await URL_QUEUE.get()
        if url is None:
            break
        # json_response = get_the_json(endpoint, params)
        json_response = url
        await RESULT_QUEUE.put(json_response)
        # add_item_to_db(endpoint, json_response)

    log.debug(f'Done {work_id}')


def clear_current_table(endpoint):
    """
    Current data only contains latest and greatest
    """
    # make new session
    session = models.Session()
    db_model = ENDPOINT_MODEL[endpoint]
    session.query(db_model).delete()
    session.commit()


async def result_reader():

    clear_current_table()

    while True:
        value = await RESULT_QUEUE.get()
        log.debug("Got value! -> {}".format(value))
        if value is None:
            break


async def fill_url_queue(endpoint, login):
    """Fill queue with urls to fetch
    """
    for i in range(100):
        await URL_QUEUE.put(f'test {i}')

    print(URL_QUEUE)


async def run_workers(endpoint, workers=WORKERS):
    """
    Run X workers processing search tasks
    """
    # start job of puting data into database
    store_data = asyncio.ensure_future(result_reader(), loop=loop)

    # get login credentials

    # for each endpoint get a list of items to pick up
    await fill_url_queue(endpoint)

    async with ClientSession() as session:
        workers = [
            asyncio.ensure_future(do_request(i, session, endpoint), loop=loop)
            for i in range(workers)]

        for _ in range(len(workers)):
            await URL_QUEUE.put(None)

        await asyncio.gather(*workers, loop=loop)

    await RESULT_QUEUE.put(None)
    await store_data
    # start x workers
    # request all details of list
    log.debug('done!')


async def main(args):
    endpoint = args.endpoint[0]
    engine = models.make_engine(section='docker')
    # models.Base.metadata.create_all(engine)
    models.set_engine(engine)
    # scrape the data!
    await run_workers(endpoint)


if __name__ == '__main__':

    desc = "Scrape API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        'endpoint', type=str,
        default='qa_realtime',
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1)

    inputparser.add_argument(
        '--dedupe',
        action='store_true',
        default=False,
        help="Remove duplicates")

    args = inputparser.parse_args()
    main(args)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
