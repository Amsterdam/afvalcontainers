
import os
import requests
import logging

# korte site codes. straatcode + huisnummer + oploopummer
BASE_DIR = os.path.dirname(__file__)
BASE_API = "https://api.data.amsterdam.nl/afval/"
BASE_API = "http://127.0.0.1:8000/afval/"

# directory met alle doeldata.
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "weegdata"))
print(DATA_PATH)

FRACTIE = 'REST'

log = logging.getLogger("weegdata")
log.setLevel(logging.DEBUG)


def site_ids():
    sites_source = open('sites_poc.txt', 'r')
    site_ids = sites_source.readlines()

    return site_ids


def get_centroid(short_id):
    """
    Get centroid for a site
    """
    url = f"{BASE_API}/v1/sites/?short_id={short_id}"

    response = requests.get(url)
    print(response)
    if response.status_code != 200:
        log.error('api call error %s', response.text)
        return None, None
    #
    data = response.json()
    lon, lat = data['results'][0]['centroid']['coordinates']
    return lon, lat


def weegdata(short_id, lon, lat, fractie):
    """
    Get all weegdata for a site
    """
    r = 0.005
    url = f"{BASE_API}/suppliers/kilogram/?location={lat},{lon},{r}"
    print(url)
    #
    response = requests.get(url)
    if response.status_code != 200:
        log.error('api call error %s', response.text)
        return
    #
    data = response.json()


def download_weegdata():
    #
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)

    all_site_ids = site_ids()

    for short_id in all_site_ids[:5]:
        lon, lat = get_centroid(short_id)
        if not lon:
            continue
        weegdata(short_id, lon, lat, FRACTIE)


if __name__ == '__main__':
    download_weegdata()
