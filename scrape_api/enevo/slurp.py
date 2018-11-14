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

assert api_config["password"]

WORKERS = 1
ENDPOINTS = ["alerts", "containers", "container_types", "container_slots",
             "sites", "site_content_types", "fill_levels"]

until = '{}Z'.format(datetime.datetime.utcnow().isoformat(timespec='seconds'))
after = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
after = '{}Z'.format(after.isoformat(timespec='seconds'))

ENDPOINT_URL = {
    "session": f"{API_URL}/session",
    "containers": f"{API_URL}/containers/?limit=0",
    "container_types": f"{API_URL}/containerTypes/?limit=0",
    "container_slots": f"{API_URL}/containerSlots/?limit=0",
    "sites": f"{API_URL}/sites/?limit=0",
    "site_content_types": f"{API_URL}/siteContentTypes/?limit=0",
    "alerts": f"{API_URL}/alerts/recent",

    "fill_levels":
        f"{API_URL}/fillLevels/?after={after}&until={until}&limit=0",

}

ENDPOINT_KEY = {
    "containers": "containers",
    "container_types": "containerTypes",
    "container_slots": "containerSlots",
    "sites": "sites",
    "site_content_types": "siteContentTypes",
    "fill_levels": "fillLevels",
    "alerts": "alerts"
}

ENDPOINT_MODEL = {
    "containers": models.EnevoContainer,
    "container_types": models.EnevoContainerType,
    "container_slots": models.EnevoContainerSlot,
    "sites": models.EnevoSite,
    "site_content_types": models.EnevoSiteContentType,
    "fill_levels": models.EnevoFillLevel,
    "alerts": models.EnevoAlert,
}

RESULT_QUEUE = asyncio.Queue()


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


async def fill_url_queue(session, endpoint):
    """Fill queue with urls to fetch."""
    url = ENDPOINT_URL[endpoint]
    url = url.format(API_URL)
    print(url)
    response = await fetch(url, session)
    json_body = await response.json()
    itemname = ENDPOINT_KEY[endpoint]

    assert itemname in json_body.keys()

    total = len(json_body[itemname])
    log.info("%s: size %s", endpoint, total)
    all_items = list(json_body[itemname])
    random.shuffle(all_items)

    for item in all_items:
        await RESULT_QUEUE.put(item)

    return total


def get_session_token():
    resp = requests.post(ENDPOINT_URL['session'], json=api_config,
                         headers={'ContentType': 'application/json'})
    return resp.json()['session']['token']


async def run_workers(endpoint):
    """Run X workers processing fetching tasks."""
    # start job of puting data into database
    store_data = asyncio.ensure_future(store_results(endpoint))
    # for endpoint get a list of items to pick up
    headers = {'X-token': get_session_token()}
    async with aiohttp.ClientSession(headers=headers) as session:
        await fill_url_queue(session, endpoint)

    await RESULT_QUEUE.put("terminate")
    await asyncio.gather(store_data)
    log.debug("done!")


async def main(endpoint, make_engine=True):
    # when testing we do not want an engine.
    if make_engine:
        engine = db_helper.make_engine(
            section="dev")
            #environment=KILO_ENVIRONMENT_OVERRIDES)
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
