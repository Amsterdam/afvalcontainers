import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DAYS = int(os.getenv("GOOGLE_DAYS", 20))
LIMIT = 2000

config_auth = configparser.RawConfigParser()
config_auth.read(BASE_DIR + "/config.ini")

TESTING = {"running": False}

# BAMMENS_API_USERNAME = os.getenv('BAMMENS_API_USERNAME')
# BAMMENS_API_PASSWORD = os.getenv('BAMMENS_API_PASSWORD')


API_URL = "https://bammensservice.nl"
