import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_auth = configparser.ConfigParser()
config_auth.read(os.path.join(BASE_DIR, "config.ini"))

TESTING = {"running": False}

# BAMMENS_API_USERNAME = os.getenv('BAMMENS_API_USERNAME')
# BAMMENS_API_PASSWORD = os.getenv('BAMMENS_API_PASSWORD')


API_BAMMENS_URL = "https://bammensservice.nl"
API_KILOGRAM_URL = "https://webservice.kilogram.nl"


KILO_ENVIRONMENT_OVERRIDES = [
    ('host', 'DATABASE_KILOGRAM_HOST'),
    ('port', 'DATABASE_KILOGRAM_PORT'),
    ('database', 'DATABASE_KILOGRAM_NAME'),
    ('username', 'DATABASE_KILOGRAM_USER'),
    ('password', 'DATABASE_KILOGRAM_PASSWORD'),
]
