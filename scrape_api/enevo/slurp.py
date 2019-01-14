"""Save external kilogram API container weigh measurements."""
import logging
import os
import asyncio
import argparse
import random
import aiohttp
import time
import datetime
import requests
import settings

from settings import API_ENEVO_URL as API_URL
from settings import KILO_ENVIRONMENT_OVERRIDES

import db_helper

from enevo import models

log = logging.getLogger("slurp_enevo")
log.setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

api_config = {
    "username": os.getenv("ENEVO_API_USERNAME", ""),
    "password": os.getenv("ENEVO_API_PASSWORD", ""),
}

assert api_config["username"], "Missing ENEVO_API_USERNAME"
assert api_config["password"], "Missing ENEVO_API_PASSWORD"

WORKERS = 6


def get_workers():
    if settings.TESTING['running']:
        return 1

    global WORKERS
    return WORKERS


RESULT_QUEUE = asyncio.Queue()
URL_QUEUE = asyncio.Queue()

ENDPOINTS = {
    "content_types": "contentTypes",
    "alerts": "alerts",
    "containers": "containers",
    "container_types": "containerTypes",
    "container_slots": "containerSlots",
    "sites": "Sites",
    "site_content_types": "siteContentTypes",
    "fill_levels": "fillLevels",
}

until = '{}Z'.format(datetime.datetime.utcnow().isoformat(timespec='seconds'))
after = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
after = '{}Z'.format(after.isoformat(timespec='seconds'))

HISTORICAL_ENDPOINTS = {
    # until - after parameter start.
    # 'alerts': ('2018-10-01T00:00:00Z'),
    'fill_levels': ('2018-10-01T00:00:00Z'),
}

ENDPOINT_URL = {
    "session": f"{API_URL}/session",
    "containers": f"{API_URL}/containers/",
    "container_types": f"{API_URL}/containerTypes/",
    "container_slots": f"{API_URL}/containerSlots/",
    "content_types": f"{API_URL}/contentTypes/",
    "sites": f"{API_URL}/sites/",
    "site_content_types": f"{API_URL}/siteContentTypes/",
    "alerts": f"{API_URL}/alerts/",
    "fill_levels": f"{API_URL}/fillLevels/",
}

ENDPOINT_KEY = {
    "containers": "containers",
    "container_types": "containerTypes",
    "container_slots": "containerSlots",
    "content_types": "contentTypes",
    "sites": "sites",
    "site_content_types": "siteContentTypes",
    "fill_levels": "fillLevels",
    "alerts": "alerts"
}

ENDPOINT_MODEL = {
    "containers": models.EnevoContainer,
    "container_types": models.EnevoContainerType,
    "container_slots": models.EnevoContainerSlot,
    "content_types": models.EnevoContentType,
    "sites": models.EnevoSite,
    "site_content_types": models.EnevoSiteContentType,
    "fill_levels": models.EnevoFillLevelRaw,
    "alerts": models.EnevoAlertRaw,
}


def prepare_object(endpoint, item):
    db_record = dict(
        # id=item['id'],
        scraped_at=datetime.datetime.now(),
        data=item,
    )

    if endpoint in HISTORICAL_ENDPOINTS:
        data_key = ENDPOINTS[endpoint]
        try:
            time = item[data_key][-1]['time']
            db_record['time'] = time
        except TypeError:
            log.debug(item[data_key])
            raise ValueError

    return db_record


def add_items_to_db(endpoint, raw_json_list):
    """Store json to database."""
    # log.debug(f"Storing {len(raw_json_list)} items")

    if not raw_json_list:
        log.error("No data recieved")
        return

    db_model = ENDPOINT_MODEL[endpoint]

    # get the session
    db_session = db_helper.session

    objects = []

    for raw_item in raw_json_list:
        objects.append(prepare_object(endpoint, raw_item))

    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()
    # log.debug(f"Stored {len(raw_json_list)} items")


async def fetch(url, session, params=None):

    assert not session.closed
    assert params

    log.debug('%s  %s', url, params)
    try:
        response = await session.get(
            url,
            compress=False,
            ssl=True,
            chunked=False,
            params=params,
        )
        return response

    except (aiohttp.client_exceptions.ServerDisconnectedError):
        log.error("Server disconnect..")
        await asyncio.sleep(random.random() * 10)
        return None


def normal_fetch(url, session, params=None):

    assert params

    log.debug('%s  %s', url, params)
    response = session.get(
        url,
        # compress=False,
        # ssl=True,
        # chunked=False,
        params=params,
    )
    return response


def clear_current_table(endpoint):
    """Clean start."""
    # make new session
    db_session = db_helper.session
    db_model = ENDPOINT_MODEL[endpoint]
    db_session.query(db_model).delete()
    db_session.commit()


async def store_results(endpoint, buffer_size=5000):

    if endpoint not in HISTORICAL_ENDPOINTS.keys():
        clear_current_table(endpoint)

    raw_results = []

    while True:
        await asyncio.sleep(0.01)
        value = await RESULT_QUEUE.get()

        if value == "terminate":
            break

        raw_results.append(value)

        if len(raw_results) > buffer_size:
            add_items_to_db(endpoint, raw_results)
            raw_results = []

    if raw_results:
        # save whats left.
        add_items_to_db(endpoint, raw_results)


async def fetch_endpoint(endpoint):
    """Fill queue with urls to fetch."""
    url = ENDPOINT_URL[endpoint]
    url = url.format(API_URL)
    log.info(url)
    store_data = asyncio.ensure_future(store_results(endpoint))

    # for endpoint get a list of items to pick up
    xtoken = get_session_token()
    headers = {
        'X-token': xtoken,
        # 'X-customer': '15220'
    }

    params = dict(cid=152202, limit=0)

    with requests.Session() as session:
        session.headers.update(headers)
        response = normal_fetch(url, session, params=params)

    json_body = response.json()
    itemname = ENDPOINT_KEY[endpoint]

    assert itemname in json_body.keys()

    total = len(json_body[itemname])
    log.info("%s: size %s", endpoint, total)
    all_items = list(json_body[itemname])

    for item in all_items:
        await RESULT_QUEUE.put(item)

    await RESULT_QUEUE.put("terminate")
    await asyncio.gather(store_data)

    return total


def check_current_date(endpoint):
    """Determine date endpoint where history is left off.

    So we can start add data from that point on.
    """
    db_session = db_helper.session
    dbmodel = models.EnevoFillLevelRaw
    record = (
        db_session
        .query(dbmodel)
        .order_by(dbmodel.time.desc())
        .first()
    )

    if record:
        return record.time

    start = HISTORICAL_ENDPOINTS[endpoint]
    # 2014-10-01T00:00:00Z
    beginning = datetime.datetime.strptime(
        f'{start}', '%Y-%m-%dT%H:%M:%SZ')
    # fall back to default.
    return beginning


async def get_session():

    session = None

    while session is None:
        try:
            xtoken = get_session_token()
            headers = {'X-token': xtoken}
            session = aiohttp.ClientSession(headers=headers)
        except (aiohttp.client_exceptions.ServerDisconnectedError):
            log.exception("Server disconnect..wait a bit")
            if session:
                await session.close()
                await asyncio.sleep(5)
                session = None

        if session:
            return session


async def get_the_json(session, endpoint, params):
    """Get some json of endpoint.

    retry x times on failure.
    """
    json = []
    response = None
    url = ENDPOINT_URL[endpoint]

    retry = 5

    retry_codes = [500, 502, 503, 504, 400]

    while retry > 0:
        await asyncio.sleep(0.01)
        json = None

        retry -= 1

        if settings.TESTING['running']:
            # no need to retry..
            retry = -1

        response = None
        try:
            response = await fetch(url, session, params=params)
        except StopIteration:
            pass

        if response is None:
            log.error("RESPONSE NONE %s %s", url, params)
            continue

        elif response.status == 200:
            log.debug(f" OK  {response.status}:{url}{params['after']}")
        elif response.status == 401:
            log.error(f" AUTH {response.status}:{url}")
            continue
        elif response.status in retry_codes:
            log.debug(f"FAIL {response.status}:{url}")
            await asyncio.sleep(0.01)
            continue

        # Sometime ENEVO throws 400 for no reason!!
        # too many request probably
        elif response.status == 400:
            log.error(response)
            log.error(await response.text())
            continue
            # raise ValueError("400. wrong request. %s", params)

        elif response.status == 404:
            log.error(f" 404 {response.status}:{url}")
            raise ValueError("404. NOT FOUND wrong request.")

        if response:
            json = await response.json()

        return json


async def load_day(session, endpoint, params):
    """Load all data within a single day."""
    # lookup key in object to look for in response
    data_key = ENDPOINTS[endpoint]

    limit = params['limit']
    count = limit

    while count == limit:

        json_response = await get_the_json(session, endpoint, params)

        if not json_response:
            # await URL_QUEUE.put(params)
            log.debug("skipping")
            count = None

        else:
            count = json_response['count']
            latest_time = json_response[data_key][-1]['time']
            until = params['until']

            after_dt = datetime.datetime.strptime(
                f'{latest_time}', '%Y-%m-%dT%H:%M:%SZ')
            before_dt = datetime.datetime.strptime(
                f'{until}', '%Y-%m-%dT%H:%M:%SZ')

            assert after_dt < before_dt, 'Time Error'

            params['after'] = latest_time

            await RESULT_QUEUE.put(json_response)


async def do_request(work_id, endpoint):
    """Download all data available for endoint item parameters.

    We do request in our own private session.
    """
    # session = None

    # for endpoint get a list of items to pick up
    headers = {
        'X-token': get_session_token(),
    }

    async with aiohttp.ClientSession(headers=headers) as session:

        while True:
            item = await URL_QUEUE.get()
            if item == "terminate":
                await session.close()
                break

            params = item
            await load_day(session, endpoint, params)

    log.debug(f"Done {work_id}")


async def log_progress():
    start = URL_QUEUE.qsize()
    while True:
        size = URL_QUEUE.qsize()
        log.info("Progress %s %s", size, start)
        await asyncio.sleep(10)


async def fetch_historical_endpoint(endpoint):
    """Fill queue with urls to fetch."""
    worker_count = get_workers()
    store_data = asyncio.ensure_future(store_results(endpoint, buffer_size=20))

    now = datetime.datetime.now()
    # see where we left off, else start from 2014.
    after = check_current_date(endpoint)
    until = after + datetime.timedelta(days=1)

    progress = asyncio.ensure_future(log_progress())
    # test hack
    log.info('Starting from %s', after)

    limit = 10000

    if settings.TESTING['running']:
        limit = 2
        now = after + datetime.timedelta(days=1)

    # fill queue with tasks
    while after < now:
        params = dict(
            after=after.strftime('%Y-%m-%dT%H:%M:%SZ'),
            until=until.strftime('%Y-%m-%dT%H:%M:%SZ'),
            cid=152202,
            limit=limit,
        )
        await URL_QUEUE.put(params)
        # move one day forward.
        after = until
        until = until + datetime.timedelta(days=1)

    workers = [
        asyncio.ensure_future(do_request(i, endpoint))
        for i in range(worker_count)]

    # Terminate instructions for all workers
    for _ in range(len(workers)):
        await URL_QUEUE.put("terminate")

    await asyncio.gather(*workers)
    await RESULT_QUEUE.put("terminate")
    await asyncio.gather(store_data)
    # wait till they are done
    progress.cancel()


class SessionException(Exception):
    pass


def get_session_token():
    resp = requests.post(
        ENDPOINT_URL['session'], json=api_config,
        headers={'ContentType': 'application/json'})

    session = resp.json().get('session')

    if not session:
        raise SessionException('Authentication Error')

    return resp.json()['session']['token']


async def run_workers(endpoint):
    """Run X workers processing fetching tasks."""
    # start job of puting data into database

    if endpoint in HISTORICAL_ENDPOINTS:
        await fetch_historical_endpoint(endpoint)
    else:
        await fetch_endpoint(endpoint)

    # wait untill all data is stored in database
    log.info("Done!")


async def main(endpoint, make_engine=True):
    # when testing we do not want an engine.
    if make_engine:
        engine = db_helper.make_engine(
            # section="docker",
            environment=KILO_ENVIRONMENT_OVERRIDES)
        db_helper.set_session(engine)
    await run_workers(endpoint)


def start_import(endpoint, make_engine=True):
    start = time.time()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(endpoint, make_engine=make_engine))
    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    desc = "Scrape Enevo API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="qa_realtime",
        choices=ENDPOINTS.keys(),
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()
    if args.debug:
        # loop.set_debug(True)
        log.setLevel(logging.DEBUG)
    endpoint = args.endpoint[0]
    start_import(endpoint)
