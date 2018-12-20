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

from settings import API_ENEVO_URL as API_URL

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

WORKERS = 1

RESULT_QUEUE = asyncio.Queue()
URL_QUEUE = asyncio.Queue()

ENDPOINTS = [
    "content_types",
    "alerts",
    "containers", "container_types", "container_slots",
    "sites", "site_content_types",
    "fill_levels"
]

until = '{}Z'.format(datetime.datetime.utcnow().isoformat(timespec='seconds'))
after = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
after = '{}Z'.format(after.isoformat(timespec='seconds'))

HISTORICAL_ENDPOINTS = {
    # until - after parameter start.
    'alerts': ('2014-10-01T00:00:00Z'),
    'fill_levels': ('2014-10-01T00:00:00Z'),
}

ENDPOINT_URL = {
    "session": f"{API_URL}/session",
    "containers": f"{API_URL}/containers/?limit=0",
    "container_types": f"{API_URL}/containerTypes/?limit=0",
    "container_slots": f"{API_URL}/containerSlots/?limit=0",
    "content_types": f"{API_URL}/contentTypes/?limit=0",
    "sites": f"{API_URL}/sites/?limit=0",
    "site_content_types": f"{API_URL}/siteContentTypes/?limit=0",

    "alerts": f"{API_URL}/alerts/",
    "fill_levels":
        f"{API_URL}/fillLevels/?after={after}&until={until}&limit=0",
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
    if endpoint == "fill_levels":
        return dict(
            time=item['time'],
            fill_level=item['fillLevel'],
            site=item['site'],
            site_name=item['siteName'],
            site_content_type=item['siteContentType'],
            confidence=item['confidence'],
            frozen=bool(item['frozen']),
        )
    return dict(
        id=item['id'],
        scraped_at=datetime.datetime.now(),
        data=item,
    )


def add_items_to_db(endpoint, json):
    """Store json to database."""
    log.debug(f"Storing {len(json)} items")

    if not json:
        log.error("No data recieved")
        return

    db_model = ENDPOINT_MODEL[endpoint]

    # get the session
    db_session = db_helper.session

    objects = []

    for item in json:
        objects.append(prepare_object(endpoint, item))

    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()
    log.debug(f"Stored {len(json)} items")


async def fetch(url, session, params=None, auth=None):
    try:
        response = await session.get(url, ssl=True)
        return response

    except (aiohttp.client_exceptions.ServerDisconnectedError):
        log.error("Server disconnect..")
        asyncio.sleep(random.random() * 10)
        return None


def clear_current_table(endpoint):
    """Clean start."""
    # make new session
    session = db_helper.session
    db_model = ENDPOINT_MODEL[endpoint]
    session.query(db_model).delete()
    session.commit()


async def store_results(endpoint):
    if endpoint != "fill_levels":
        clear_current_table(endpoint)

    results = []

    while True:
        value = await RESULT_QUEUE.get()

        if value == "terminate":
            break

        results.append(value)

        if len(results) > 25:
            add_items_to_db(endpoint, results)
            results = []

    if results:
        # save whats left.
        add_items_to_db(endpoint, results)


async def fetch_endpoint(session, endpoint):
    """Fill queue with urls to fetch."""
    url = ENDPOINT_URL[endpoint]
    url = url.format(API_URL)
    log.info(url)
    response = await fetch(url, session)
    json_body = await response.json()
    itemname = ENDPOINT_KEY[endpoint]

    assert itemname in json_body.keys()

    total = len(json_body[itemname])
    log.info("%s: size %s", endpoint, total)
    all_items = list(json_body[itemname])
    # random.shuffle(all_items)

    for item in all_items:
        await RESULT_QUEUE.put(item)

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


async def do_request(work_id, endpoint, params={}):
    """WIP Do request in our own private session."""
    count = 0
    session = None

    while True:

        if not session:
            # session = ClientSession()
            # set login credentials in session
            try:
                await # login.set_login_cookies(session)
            except (aiohttp.client_exceptions.ServerDisconnectedError):
                log.exception("Server disconnect..wait a bit")
                await session.close()
                asyncio.sleep(5)
                session = None
                continue

        item = await URL_QUEUE.get()

        if item == "terminate":
            await session.close()
            break

        # url = ENDPOINT_URL[endpoint]
        _id = item["id"]
        json_response = await get_the_json(session, endpoint, _id)

        if not json_response:
            URL_QUEUE.put(item)
            log.debug("skipping")
            continue

        _type = list(json_response.keys())[0]
        item = json_response[_type]
        await RESULT_QUEUE.put(item)

        count += 1
        if count > 40:
            await session.close()
            session = None
            count = 0

    log.debug(f"Done {work_id}")


async def fetch_historical_endpoint(session, endpoint):
    """Fill queue with urls to fetch."""
    after = check_current_date(endpoint)
    # before = after + datetime.timedelta(days=1)
    # pass
    import q; q.d()
    # determine start date
    # derived from current data in db or default.

    # fetch data in chunks of 10.000


def get_session_token():
    resp = requests.post(
        ENDPOINT_URL['session'], json=api_config,
        headers={'ContentType': 'application/json'})

    session = resp.json().get('session')

    if not session:
        raise Exception('Authentication Error')

    return resp.json()['session']['token']


async def run_workers(endpoint):
    """Run X workers processing fetching tasks."""
    # start job of puting data into database
    store_data = asyncio.ensure_future(store_results(endpoint))
    # for endpoint get a list of items to pick up
    headers = {'X-token': get_session_token()}
    async with aiohttp.ClientSession(headers=headers) as session:

        if endpoint in HISTORICAL_ENDPOINTS:
            await fetch_historical_endpoint(session, endpoint)
        else:
            await fetch_endpoint(session, endpoint)

    await RESULT_QUEUE.put("terminate")
    await asyncio.gather(store_data)
    log.debug("done!")


async def main(endpoint, make_engine=True):
    # when testing we do not want an engine.
    if make_engine:
        engine = db_helper.make_engine(
            section="docker")
        # environment=KILO_ENVIRONMENT_OVERRIDES)
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
        choices=ENDPOINTS,
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
