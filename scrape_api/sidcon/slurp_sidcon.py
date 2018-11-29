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
from sidcon.models import SidcomRaw
from sidcon.models import SidcomFillLevel

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

ALL_ID_NUMBERS = set()


def get_container_ids():
    """Get container ids from API."""
    environment = os.environ.get('ENVIRONMENT', 'acceptance')
    url = API_URLS[environment]

    FULL_URL = f'{url}/afval/containers/'
    params = dict(
        fields='id_number',
        page_size=18000,
        format='json'
    )
    r = requests.get(FULL_URL, params=params)
    all_containers = r.json()

    for item in all_containers['results']:
        ALL_ID_NUMBERS.add(item['id_number'])

    LOG.info('Found %s ids', len(ALL_ID_NUMBERS))


def store_raw_response(raw_json):
    db_session = db_helper.session
    db_model = SidcomRaw
    objects = []
    scraped_at = datetime.datetime.now()
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
    LOG.info('storing..')
    db_session = db_helper.session
    db_model = SidcomFillLevel

    scraped_at = snapshot.scraped_at
    rawdata = snapshot.data
    # rawdata = json.loads(rawdata)

    objects = []

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
            if container_state['description'] in ALL_ID_NUMBERS:
                container_state['valid'] = True
            container_state = set_geometrie(container_state)
            grj = dict(scraped_at=scraped_at, **container_state)
            objects.append(grj)

    # TODO join states with 'official' containers / sites
    db_session.bulk_insert_mappings(db_model, objects)
    db_session.commit()


def _get_latest_inserts():
    """Get lastest insert since we last copied to API."""
    db_session = db_helper.session
    latest = (
        db_session.query(SidcomFillLevel)
        .order_by(SidcomFillLevel.scraped_at.desc())
        .first()
    )

    if latest:
        # update since api
        new_states = (
            db_session.query(SidcomRaw)
            .order_by(SidcomRaw.scraped_at.desc())
            .filter(SidcomRaw.scraped_at > latest.scraped_at)
        )
    else:
        # empty api.
        new_states = (
            db_session.query(SidcomRaw).all()
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
