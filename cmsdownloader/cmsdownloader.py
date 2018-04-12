"""
Download all containers from Bammens Api,
for more info: https://bammensservice.nl/api/doc

credentials are in rattic
"""
# utf-8
import os
import logging
import requests
import argparse
import json
import tenacity
import login


logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S')

log = logging.getLogger(__name__)

assert os.environ['BAMMENS_API_USERNAME']
assert os.environ['BAMMENS_API_PASSWORD']


@tenacity.retry(wait=tenacity.wait_fixed(1),
                retry=tenacity.retry_if_exception_type(IOError))
def getItem(session, cookies, endpoint, _id):
    """Get The container data"""
    url = baseUrl + '/api/' + endpoint + '/' + str(_id) + '.json'
    containerURI = session.get(url, cookies=cookies)
    containerData = containerURI.json()
    return containerData


def main(baseUrl, endpoints, folder):
    """Get Containers."""

    with requests.Session() as session:
        cookies = login.get_cookies(session, baseUrl)

        for endpoint in endpoints:
            data = []
            url = baseUrl + '/api/' + endpoint + '.json'

            log.info('Retrieving all objects from %s', endpoint)
            ListURI = session.get(url, cookies=cookies)
            List = ListURI.json()
            arrayName = list(List.keys())[0]

            IdList = [item['id'] for item in List[arrayName]]
            for i, Id in enumerate(IdList):
                if i % 30 == 0:
                    log.info('%d of %d Done', i, len(IdList))
                item = getItem(session, cookies, endpoint, Id)
                data.append(item)
            filepath = folder + '/' + endpoint + '.json'

            with open(filepath, 'w') as outFile:
                json.dump(data, outFile, indent=2)
                log.info('Written file: {}', filepath)

        log.info('Done with downloading!')


if __name__ == '__main__':
    desc = "Download all containers from Bammens Api, for more info: https://bammensservice.nl/api/doc"   # noqa
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('datadir', type=str,
                        help='Local data directory.')
    args = parser.parse_args()

    baseUrl = 'https://bammensservice.nl'
    endpoints = ['containertypes', 'containers', 'wells']

    main(baseUrl, endpoints, args.datadir)
