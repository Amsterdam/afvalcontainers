import os
import configparser
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_auth = configparser.ConfigParser()
config_auth.read(os.path.join(BASE_DIR, "config.ini"))


ALEMBIC = os.path.join(BASE_DIR, "alembic.ini")

Base = declarative_base()

TESTING = {"running": False}

# BAMMENS_API_USERNAME = os.getenv('BAMMENS_API_USERNAME')
# BAMMENS_API_PASSWORD = os.getenv('BAMMENS_API_PASSWORD')

API_BAMMENS_URL = "https://bammensservice.nl"
API_KILOGRAM_URL = "https://webservice.kilogram.nl"
API_ENEVO_URL = "https://api.enevo.com/api/3"


KILO_ENVIRONMENT_OVERRIDES = [
    ('host', 'DATABASE_KILOGRAM_HOST'),
    ('port', 'DATABASE_KILOGRAM_PORT'),
    ('database', 'DATABASE_KILOGRAM_NAME'),
    ('username', 'DATABASE_KILOGRAM_USER'),
    ('password', 'DATABASE_KILOGRAM_PASSWORD'),
]
