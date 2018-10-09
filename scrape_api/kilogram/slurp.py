"""Save external kilogram API container weigh measurements."""
import logging
import os
import asyncio
import argparse
import random
import aiohttp
import time
import json
import datetime

from settings import API_KILOGRAM_URL as API_URL

import db_helper
from kilogram import models

log = logging.getLogger("slurp_bammens")
log.setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

api_config = {
    "password": os.getenv("KILOGRAM_API_PASSWORD", ""),
    "hosts": {"production": "https://bammens.nl/api/"},
    # 'port': 3001,
    "username": os.getenv("KILOGRAM_API_USERNAME", "amsterdam"),
}

WORKERS = 4
STATUS = {"done": False}
ENDPOINT = "amsterdam/api.php"
API_ENDPOINT = f'{API_URL}/{ENDPOINT}'
URL_QUEUE = asyncio.Queue()
RESULT_QUEUE = asyncio.Queue()

assert api_config['password'], "KILOGRAM_API_PASSWORD not set"
AUTH = (api_config["username"], api_config["password"])


async def add_items_to_db(weigh_measurements):
    """Store json to database."""
    if not weigh_measurements:
        log.error("No data recieved")
        return

    fields = weigh_measurements['Fields']
    records = weigh_measurements['Records']

    log.debug(f"Store {len(records)} measurements")

    db_model = models.KilogramRaw

    # get the session
    db_session = db_helper.session

    objects = []
    # Store the location json!
    scraped_at = datetime.datetime.now()

    dateidx = fields.index('Date')
    timeidx = fields.index('Time')
    sysidx = fields.index('SystemId')

    date = records[-1][dateidx]
    time = records[-1][timeidx]
    system_id = records[-1][sysidx]

    weigh_at = datetime.datetime.strptime(
        f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    grj = dict(
        weigh_at=weigh_at,
        system_id=system_id,
        scraped_at=scraped_at, data=weigh_measurements)

    objects.append(grj)

    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()
    log.debug(f"Stored {len(records)} measurements")


async def fetch(url, body, session):
    """Fetch url with session."""
    body = json.dumps(body)
    try:
        response = await session.post(url, data=body, ssl=True)
        return response
    except (aiohttp.client_exceptions.ServerDisconnectedError):
        log.error("Server disconnect..")
        asyncio.sleep(random.random() * 10)
        return None


async def store_results():
    """Store json in database."""
    while True:
        measurements = await RESULT_QUEUE.get()

        if measurements == "terminate":
            break

        await add_items_to_db(measurements)


async def log_progress(total):
    while True:
        size = URL_QUEUE.qsize()
        log.info("Progress %s %s", size, total)
        await asyncio.sleep(10)


async def fill_url_queue(session):
    """Fill queue with urls to fetch.

    We collect for each weigh system all measurements
    """
    body = {'request': 'getSystems'}
    response = await fetch(API_ENDPOINT, body, session)
    json_body = await response.json()
    assert json_body['Status'] == "SUCCESSFUL"
    total = len(json_body['Systems'])
    log.info("Found systems %s", total)
    all_items = list(json_body['Systems'])
    random.shuffle(all_items)
    for i in all_items:
        await URL_QUEUE.put(i)
    # await URL_QUEUE.put(220)
    # return 1
    return total


async def get_the_json(session, body, count) -> list:
    """
    Parse some json from post request with given body.

    retry x times on failure
    return json
    """
    json = []
    params = {}
    response = None
    url = ENDPOINT

    retry = 5

    retry_codes = [500, 502, 503, 504]

    while retry > 0:
        json = None
        retry -= 1
        response = await fetch(API_ENDPOINT, body, session)

        if response is None:
            log.error("RESPONSE NONE %s %s", url, params)
            continue

        elif response.status == 200:
            log.debug(
                f" OK  {response.status}:{url} {body['Systems'][0]}" +
                f" {body.get('StartDate')} {count}"
            )
        elif response.status == 401:
            log.error(f"AUTH {response.status}:{url}")
        elif response.status in retry_codes:
            log.debug(f"FAIL {response.status}:{url}")
            continue

        # WE did WRONG requests. crash hard!
        elif response.status == 400:
            log.error(f" 400 {response.status}:{url}")
            raise ValueError("400. wrong request.")

        elif response.status == 404:
            log.error(f" 404 {response.status}:{url}")
            raise ValueError("404. NOT FOUND wrong request.")

        if response:
            json = await response.json()

        return json


def get_start_time(system_id):
    """Find out date and time of latest system measurement."""
    # get the session
    db_session = db_helper.session

    KilogramRaw = models.KilogramRaw
    record = (
        db_session
        .query(KilogramRaw)
        .filter(KilogramRaw.system_id == system_id)
        .order_by(KilogramRaw.weigh_at.desc())
        .first()
    )

    if record:
        date = record.weigh_at.strftime('%Y-%m-%d')
        time = record.weigh_at.strftime('%H:%M:%S')
        return date, time

    return None, None


async def load_system_weigh_data(session, system_id):
    """Fetch for one system all pending weigh data."""
    count = 0
    json_response = None

    # check where we left off for system_id
    start_date, start_time = get_start_time(system_id)

    while True:

        body = {
            'request': 'getWeighData',
            'Systems': [int(system_id)],
            'Limit': 1000
        }

        if start_time and start_date:
            body['StartDate'] = start_date
            body['StartTime'] = start_time

        json_response = await get_the_json(session, body, count)

        if not json_response:
            URL_QUEUE.put(system_id)
            log.debug("skipping / delay")
            continue

        records = json_response.get('Records', [])

        if not records:
            # no records returned we are done.
            return

        await RESULT_QUEUE.put(json_response)

        if len(records) < 1000:
            # no full page of records returned
            # so we should be done.
            return

        # update start date and start time
        json_response['Records'][-1]
        fields = json_response['Fields']
        dateidx = fields.index('Date')
        timeidx = fields.index('Time')
        start_date = records[-1][dateidx]
        start_time = records[-1][timeidx]
        count += 1


async def load_weigh_data(work_id, params={}):
    """Do request in our own private worker session."""
    session = None
    auth = aiohttp.BasicAuth(login=AUTH[0], password=AUTH[1])

    while True:
        if not session:
            session = aiohttp.ClientSession(auth=auth)

        # pick a system id.
        system_id = await URL_QUEUE.get()

        if system_id == "terminate":
            await session.close()
            break

        await load_system_weigh_data(session, system_id)

    log.debug(f"Done {work_id}")


async def run_workers(workers=WORKERS):
    """Run X workers processing fetching tasks."""
    # start job of puting data into database
    store_data = asyncio.ensure_future(store_results())
    # for endpoint get a list of items to pick up

    auth = aiohttp.BasicAuth(login=AUTH[0], password=AUTH[1])
    async with aiohttp.ClientSession(auth=auth) as session:
        # await login.set_login_cookies(session)
        total = await fill_url_queue(session)

    progress = asyncio.ensure_future(log_progress(total))

    log.info("Starting %d workers", workers)

    workers = [
        asyncio.ensure_future(load_weigh_data(i))
        for i in range(workers)]

    # Terminate instructions for all workers
    for _ in range(len(workers)):
        await URL_QUEUE.put("terminate")

    # wait till they are done
    await asyncio.gather(*workers)
    progress.cancel()
    await RESULT_QUEUE.put("terminate")
    # wait untill all data is stored in database
    await asyncio.gather(store_data)
    # start x workers
    # request all details of list
    log.debug("done!")


async def main(workers=WORKERS, make_engine=True):
    # when testing we do not want an engine.
    if make_engine:
        engine = db_helper.make_engine(section="docker")
        db_helper.set_session(engine)
    await run_workers(workers=workers)


def start_import(workers=WORKERS, make_engine=True):
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(workers=workers, make_engine=make_engine))
    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":

    desc = "Scrape Kilogram API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()
    if args.debug:
        # loop.set_debug(True)
        log.setLevel(logging.DEBUG)
    start_import()
