"""Create login session with cookies for sidcon API."""


import requests
import hashlib
import os
import json
import logging

from settings import BASE_DIR
# from aiohttp import ClientSession

LOG = logging.getLogger(__name__)
BASE_URL = 'https://sidconpers2.mic-o-data.nl'

# def store_response(raw_json):
#
#    scraped_at = datetime.datetime.now()
#
#    grj = dict(
#        system_id=system_id,
#        scraped_at=scraped_at, data=weigh_measurements)
#
#    objects.append(grj)
#
#    db_session.bulk_insert_mappings(db_model, objects)
#    db_session.commit()


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
            LOG.error("Loading current container state")
            response2 = s.post(BASE_URL + '/Direct/Router', json=rpc)

            if response.status_code == 200:
                LOG.error("OK")
            else:
                LOG.error("SIDCON API CALL FAILED")
                raise Exception("SIDCON API FAILED")

            print(response2.status_code)


get_sidcon_container_status()
# klogin()
