import os
import configparser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DAYS = int(os.getenv('GOOGLE_DAYS', 20))
LIMIT = 2000

AUTH_ROOT = os.path.abspath(os.path.join(BASE_DIR))
config_auth = configparser.RawConfigParser()
config_auth.read(AUTH_ROOT + '/scrape_api/config.ini')

TESTING = {
    'running': False
}

BAMMENS_API_USERNAME = os.getenv('BAMMENS_API_USERNAME')
BAMMENS_API_PASSWORD = os.getenv('BAMMENS_API_PASSWORD')


API_URL = 'https://bammensservice.nl'
