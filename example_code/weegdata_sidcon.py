
import os
import requests
import logging

# korte site codes. straatcode + huisnummer + oploopummer
BASE_DIR = os.path.dirname(__file__)
BASE_API = "https://api.data.amsterdam.nl/afval"
BASE_API = "http://127.0.0.1:8000/afval"

# directory met alle doeldata.
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "weegdata"))
print(DATA_PATH)

FRACTIE = ''  # Alle fracties
# FRACTIE = 'Rest'
# FRACTIE = 'Glas'
# FRACTIE = 'Papier'
# FRACTIE = 'Textiel'
# FRACTIE = 'Plastic'

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.ERROR)
log = logging.getLogger("weegdata")
log.setLevel(logging.DEBUG)


def site_ids():
    sites_source = open('sites_poc.txt', 'r')
    site_ids = sites_source.readlines()
    return site_ids


def get_sidcon_sites():
    """Extract all sites with a sidcon container.
    """
    # search all sidcon types.
    # https://api.data.amsterdam.nl/afval/v1/containertypes/?search=Sidcon

    # get all site_ids for a given container type name.
    # https://api.data.amsterdam.nl/afval/v1/sites/?container_type=Sidcon+pers+Rest+5m3&fields=short_id

    url = f"{BASE_API}/v1/containertypes/"
    response = requests.get(
        url,
        {'search': "Sidcon"}
    )

    data = response.json()
    types = data['results']
    type_names = []
    for t in types:
        type_names.append(t['name'])

    log.debug(type_names)
    url = f"{BASE_API}/v1/sites/"
    site_ids = []
    for name in type_names:
        response = requests.get(
            url,
            {
                'container_type': name,
                'fields': 'short_id',
                'page_size': 1000
            }
        )
        data = response.json()
        log.debug(len(data['results']))
        for item in data['results']:
            site_ids.append(str(item['short_id']))

    print(site_ids)

    return site_ids


def get_centroid(short_id):
    """
    Get centroid for a site
    """
    url = f"{BASE_API}/v1/sites/?short_id={short_id}"

    response = requests.get(url)
    if response.status_code != 200:
        log.error('api call error %s', response.text)
        return None, None
    #
    data = response.json()
    results = data['results']
    if not results:
        log.error('site missing %s', short_id)
        return None, None
    lon, lat = data['results'][0]['centroid']['coordinates']
    return lon, lat


def weegdata(short_id, lon, lat, fractie):
    """
    Get all weegdata for a site.

    We look for all measurements near a site
    """
    r = 17  # 17 meter.
    url = f"{BASE_API}/suppliers/kilogram/"

    params = {
        "location": f"{lon},{lat},{r}",
        "page_size": 15000,
        "format": "csv",
        # "fractie": "Rest",
    }
    if FRACTIE:
        params['fractie'] = FRACTIE
    response = requests.get(url, params=params)
    if response.status_code != 200:
        log.error('api call error %s', response.text)
        return
    #
    data = response.text
    fractie_name = 'allefracties'
    if FRACTIE:
        fractie_name = FRACTIE
    csv_file = f"weegdata_{fractie_name}_{lon:.5f}_{lat:.5f}_{r}m_site_{short_id}.csv"   # noqa
    log.info('Writing to %s', csv_file)
    weegdatacsv = os.path.join(DATA_PATH, csv_file)
    target = open(weegdatacsv, 'w')
    target.write(data)


def download_weegdata():
    #
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)

    all_site_ids = get_sidcon_sites()

    for short_id in all_site_ids:
        short_id = short_id.strip()
        lon, lat = get_centroid(short_id)
        if not lon:
            continue
        weegdata(short_id, lon, lat, FRACTIE)


if __name__ == '__main__':
    download_weegdata()
