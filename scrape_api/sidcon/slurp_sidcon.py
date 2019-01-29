"""Collect Pers-container Status.

There are about ~280 (11-2018) to
the internet connected perscontainers.

store the actual status and keep history.


Steps:

- Create login session with cookies for sidcon API.
- Store raw status
- Copy status into API database table
- Keep track of history

"""

import re
import os
import argparse
import requests
import hashlib
import json
import logging
import datetime
import db_helper
from sidcon.models import SidconRaw
from sidcon.models import SidconFillLevel

from settings import KILO_ENVIRONMENT_OVERRIDES
from settings import BASE_DIR
# from aiohttp import ClientSession

LOG = logging.getLogger(__name__)
BASE_URL = 'https://sidconpers2.mic-o-data.nl'

API_URLS = {
    'acceptance': 'http://acc.api.data.amsterdam.nl',
    # 'acceptance': 'https://acc.api.data.amsterdam.nl',
    'production': 'https://api.data.amsterdam.nl'
}

ALL_ID_NUMBERS = {}


PATTERN = re.compile(r'\s+')


def remove_white_space(long_id_code):
    long_id_code = re.sub(PATTERN, '', long_id_code)
    return long_id_code


def fetch_api_containers():

    environment = os.environ.get('ENVIRONMENT', 'acceptance')
    url = API_URLS[environment]

    container_list = []

    page_size = 3000

    params = dict(
        fields='id_number,well.site.short_id',
        expand='well.site',
        page_size=page_size,
        format='json',
        page=1
    )

    FULL_URL = f'{url}/afval/v1/containers/'
    while True:
        with requests.Session() as s:
            r = s.get(FULL_URL, params=params)
            assert r.status_code == 200
            containers = r.json()

            if len(containers['results']) == page_size:
                params['page'] += 1
            else:
                break

            container_list.extend(containers['results'])

    return container_list


def get_container_ids():
    """Get container ids from afval api API.

    The fill-level historical data lives in its own KILOGRAM database
    so we cannot do a simple join. We just use our own API.
    """
    all_containers = fetch_api_containers()

    for item in all_containers:
        if not item:
            continue
        if 'id_number' not in item:
            LOG.error(item.items())
            continue
        container_id = remove_white_space(item['id_number'])

        well = item.get('well')

        if not well:
            LOG.error(item)
            continue

        site = well.get('site', {})
        if not site:
            LOG.error(site)
            continue

        site_short_id = site.get('short_id')

        ALL_ID_NUMBERS[container_id] = site_short_id

    LOG.info('Found %s ids', len(ALL_ID_NUMBERS))


def store_raw_response(raw_json):
    db_session = db_helper.session
    db_model = SidconRaw
    objects = []
    scraped_at = datetime.datetime.now()
    assert raw_json
    grj = dict(scraped_at=scraped_at, data=raw_json)
    objects.append(grj)
    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def validate_ints(container_state):
    int_fields = ['house_number', 'press_status']

    for field in int_fields:
        value = container_state.get(field)

        if value is None:
            continue
        try:
            int(value)
        except ValueError:
            container_state[field] = None

    return container_state


def _snake_case_dict(container_state: dict):
    """Convert Camelcase to snake_case."""
    new_dict = {}

    assert len(container_state)

    for k, v in container_state.items():
        k = convert_to_snake(k)
        new_dict[k] = v

    return new_dict


def set_geometrie(container_state: dict):

    try:
        lon = float(container_state.get('lon', 0))
        lat = float(container_state.get('lat', 0))
    except (ValueError, TypeError):
        lon, lat = 0, 0
        LOG.debug(
            'LON LAT ERROR %s %s %s',
            container_state['_id'],
            container_state['description'],
            container_state['street'],
        )

    if lon and lat:
        geometrie = f"SRID=4326;POINT({lon} {lat})"
    else:
        geometrie = None  # f"SRID=4326;POINT(0 0)"

    container_state['geometrie'] = geometrie
    return container_state


def _store_single_container_states(snapshot):
    db_session = db_helper.session
    db_model = SidconFillLevel

    scraped_at = snapshot.scraped_at
    rawdata = snapshot.data
    # rawdata = json.loads(rawdata)

    objects = []
    LOG.info('storing..%s', scraped_at)

    for rpc_response in rawdata:
        for single_state in rpc_response['result'].get('data', []):
            assert type(single_state) is dict
            container_state = _snake_case_dict(single_state)
            container_state = validate_ints(container_state)

            # skip this invalid record type
            if container_state.get('container_id', 0) == 0:
                continue

            _id = container_state.pop('id')
            container_state['_id'] = _id
            container_state['valid'] = False
            description = container_state['description']
            description = remove_white_space(description)
            if description in ALL_ID_NUMBERS:
                container_state['valid'] = True
                container_state['site_id'] = ALL_ID_NUMBERS[description]
            # remove white space from key.
            container_state['description'] = description

            container_state = set_geometrie(container_state)
            grj = dict(scraped_at=scraped_at, **container_state)
            objects.append(grj)

    # TODO join states with 'official' containers / sites
    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()


def _get_latest_inserts():
    """Get lastest inserts since we last copied to API."""
    db_session = db_helper.session
    latest = (
        db_session.query(SidconFillLevel)
        .order_by(SidconFillLevel.scraped_at.desc())
        .first()
    )

    if latest:
        # update since api
        new_states = (
            db_session.query(SidconRaw)
            .order_by(SidconRaw.scraped_at.desc())
            .filter(SidconRaw.scraped_at > latest.scraped_at)
        )
    else:
        # empty api.
        new_states = (
            db_session.query(SidconRaw).all()
        )

    return new_states


def store_container_status_in_api():
    # db_session = db_helper.session

    new_states = _get_latest_inserts()

    get_container_ids()

    for snapshot in new_states:
        # import container states
        _store_single_container_states(snapshot)


def get_sidcon_container_status():
    password = os.environ.get('SIDCON_PASSWORD', '')
    password = password.encode('UTF-8')

    if not password:
        raise Exception('SIDCON_PASSWORD missing')

    encrypted = hashlib.sha1(password).hexdigest()
    passstr = f"-[encrypted]-{encrypted}"

    data = {
        'TaskId': 238,
        'UserName': 'wieren',
        'Password': passstr
    }

    with requests.Session() as s:

        response = s.post(
            BASE_URL + '/Account/LogOn', data=data)

        if response.status_code == 200:
            LOG.info("Login succesfull")
        else:
            LOG.error("Login FAILED")
            raise Exception("SIDCON LOGIN FAILED")

        with open(BASE_DIR + "/sidcon/rpc.json") as rpcjsonfile:
            rpcjson = rpcjsonfile.read()
            rpc = json.loads(rpcjson)
            LOG.info("Loading current container state")
            response2 = s.post(BASE_URL + '/Direct/Router', json=rpc)

            if response2.status_code == 200:
                LOG.info("OK %s", response2.status_code)
            else:
                LOG.error("SIDCON API CALL FAILED")
                raise Exception("SIDCON API FAILED")

            store_raw_response(response2.json())


if __name__ == "__main__":
    desc = "Load percontainer states."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--slurp",
        action="store_true",
        default=False, help="Store latest state"
    )

    inputparser.add_argument(
        "--copy",
        action="store_true",
        default=False, help="Copy latest state to API"
    )

    inputparser.add_argument(
        "--getids",
        action="store_true",
        default=False, help="Copy latest state to API"
    )

    args = inputparser.parse_args()

    engine = db_helper.make_engine(
        section="docker",
        environment=KILO_ENVIRONMENT_OVERRIDES)
    db_helper.set_session(engine)

    if args.slurp:
        get_sidcon_container_status()
    if args.copy:
        store_container_status_in_api()
    if args.getids:
        get_container_ids()
