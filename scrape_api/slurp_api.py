"""
Save external bammens API container sources
"""

import aiohttp
import random
import time
import dateparser
# import aiopg
from aiohttp import ClientSession
import asyncio

import datetime
import os
import models
import logging
import argparse
import settings
from settings import API_URL
import os.path
from dateutil import parser

import login

log = logging.getLogger('slurp_api')
log.setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.ERROR)

ENVIRONMENT = os.getenv('ENVIRONMENT', 'acceptance')

WORKERS = 3

STATUS = {
    'done': False
}

URL_QUEUE = asyncio.Queue()
RESULT_QUEUE = asyncio.Queue()

ENDPOINTS = [
    'container_types',
    'containers',
    'wells'
]

ENDPOINT_MODEL = {
    'container_types': models.ContainerType,
    'containers': models.Container,
    'wells': models.Well
}

ENDPOINT_URL = {
    'container_types': f'{API_URL}/api/containertypes',
    'wells': f'{API_URL}/api/wells',
    'containers': f'{API_URL}/api/containers',
}


api_config = {
    'password': os.getenv('BAMMENS_API_PASSWORD', ''),
    'hosts': {
        'production': 'https://bammens.nl/api/',
    },
    # 'port': 3001,
    'username': os.getenv('BAMMENS_API_USERNAME', '')
}


AUTH = (api_config['username'], api_config.get('password'))


async def fetch(url, session, params=None, auth=None):
    try:
        response = await session.get(url, ssl=True)
        return response
    except(aiohttp.client_exceptions.ServerDisconnectedError):
        log.error('Server disconnect..')
        asyncio.sleep(random.random() * 10)
        return None


async def get_the_json(session, endpoint, _id=None) -> list:
    """
    Get some json of endpoint!

    retry x times on failure
    return json
    """
    json = []
    params = {}
    response = None
    url = ENDPOINT_URL[endpoint]
    if _id:
        url = f'{url}/{_id}.json'

    retry = 5

    retry_codes = [500, 502, 503, 504]

    while retry > 0:
        json = None
        retry -= 1
        response = await fetch(url, session)

        if response is None:
            log.error('RESPONSE NONE %s %s', url, params)
            continue
        elif response.status == 200:
            log.debug(f' OK  {response.status}:{url}')
        elif response.status == 401:
            log.error(f' AUTH {response.status}:{url}')
        elif response.status in retry_codes:
            log.debug(f'FAIL {response.status}:{url}')
            continue
        # WE did WRONG requests. crash hard!
        elif response.status == 400:
            log.error(f' 400 {response.status}:{url}')
            raise ValueError('400. wrong request.')
        elif response.status == 404:
            log.error(f' 404 {response.status}:{url}')
            raise ValueError('404. NOT FOUND wrong request.')

        if response:
            json = await response.json()

        return json


def add_items_to_db(endpoint, json: list):
    """
    Given json api response, store data in database
    """

    if not json:
        log.error('No data recieved')
        return

    db_model = ENDPOINT_MODEL[endpoint]

    # make new session
    db_session = models.session

    # Store the location json!
    for item in json:

        scraped_at = datetime.datetime.now()

        grj = db_model(
            id=item['id'],
            scraped_at=scraped_at,
            data=item,
        )
        db_session.add(grj)

    db_session.commit()

    log.debug(f"Stored {len(json)} items")


async def do_request(work_id, endpoint, params={}):
    """
    Do request in our own private session
    """
    count = 0
    session = None

    while True:

        if not session:
            session = ClientSession()
            # set login credentials in session
            try:
                await login.set_login_cookies(session)
            except(aiohttp.client_exceptions.ServerDisconnectedError):
                log.exception('Server disconnect..wait a bit')
                await session.close()
                asyncio.sleep(5)
                session = None
                # try again
                continue

        item = await URL_QUEUE.get()

        if item == 'terminate':
            break

        url = ENDPOINT_URL[endpoint]
        _id = item['id']
        json_response = await get_the_json(session, endpoint, _id)

        if not json_response:
            URL_QUEUE.put(item)
            log.debug('skipping')
            continue

        _type = list(json_response.keys())[0]
        item = json_response[_type]
        cleaned = validate_timestamps(item)
        await RESULT_QUEUE.put(cleaned)

        count += 1
        if count > 40:
            await session.close()
            session = None
            count = 0

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


def validate_timestamps(item):
    """We recieve invalid timestamps
    so we clean them up here.
    """
    timestamp_keys = [
        'created_at', 'placing_date', 'warranty_date',
        'operational_date',
    ]

    for key in timestamp_keys:
        date = item.get(key)
        if not date:
            continue
        d = dateparser.parse(date)
        if not d:
            log.error('Invalid %s %s %s', key, date, item['id'])
            item[key] = None

    return item


async def store_results(endpoint):

    clear_current_table(endpoint)

    results = []
    while True:
        value = await RESULT_QUEUE.get()

        if value == 'terminate':
            break

        results.append(value)
        if len(results) > 5:
            # save items
            add_items_to_db(endpoint, results)
            results = []

    if results:
        # save whats left.
        add_items_to_db(endpoint, results)


async def log_progress(total):
    while True:
        size = URL_QUEUE.qsize()
        log.info('Progress %s %s', size, total)
        await asyncio.sleep(10)


async def fill_url_queue(session, endpoint):
    """Fill queue with urls to fetch
    """
    url = ENDPOINT_URL[endpoint]
    url = url.format(API_URL)
    response = await fetch(url, session)
    json_body = await response.json()
    total = len(json_body[endpoint])
    log.info('%s: size %s', endpoint, total)
    all_items = list(json_body[endpoint])
    random.shuffle(all_items)
    for i in all_items:
        await URL_QUEUE.put(i)
    return total


async def run_workers(endpoint, workers=WORKERS):
    """Run X workers processing fetching tasks
    """
    # start job of puting data into database
    store_data = asyncio.ensure_future(store_results(endpoint))
    # for endpoint get a list of items to pick up

    async with ClientSession() as session:
        await login.set_login_cookies(session)
        total = await fill_url_queue(session, endpoint)

    progress = asyncio.ensure_future(log_progress(total))

    log.info('Starting %d workers %s', workers, endpoint)

    workers = [
        asyncio.ensure_future(do_request(i, endpoint))
        for i in range(workers)]

    # Terminate instructions for all workers
    for _ in range(len(workers)):
        await URL_QUEUE.put('terminate')

    # wait till they are done
    await asyncio.gather(*workers)
    progress.cancel()

    await RESULT_QUEUE.put('terminate')
    # wait untill all data is stored in database
    await asyncio.gather(store_data)
    # start x workers
    # request all details of list
    log.debug('done!')


async def main(endpoint, workers=WORKERS, make_engine=True):
    # when testing we do not want an engine.
    if make_engine:
        engine = models.make_engine(section='docker')
        models.set_engine(engine)
    await run_workers(endpoint, workers=workers)


def start_import(args, workers=WORKERS, make_engine=True):
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(args, workers=workers, make_engine=make_engine))
    log.info('Took: %s', time.time() - start)


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
        '--debug',
        action='store_true',
        default=False,
        help="Enable debugging")

    args = inputparser.parse_args()
    if args.debug:
        # loop.set_debug(True)
        log.setLevel(logging.DEBUG)
    endpoint = args.endpoint[0]
    start_import(endpoint)
