"""Some webservice.kilogram.nl tests."""

import json
# import time
import unittest
import asynctest
from kilogram import slurp
from kilogram import models
from kilogram import copy_to_model

import db_helper
import logging
from settings import BASE_DIR
from settings import TESTING

log = logging.getLogger(__name__)

FIX_DIR = BASE_DIR

transaction = []
connection = []
engine = []
session = []


def setup_module():
    global transaction, connection, engine, session
    TESTING["running"] = True
    db_helper.create_db()
    engine = db_helper.make_engine(section="test")
    connection = engine.connect()
    transaction = connection.begin()
    session = db_helper.set_session(engine)
    session.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    session.commit()
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


def teardown_module():
    global transaction, connection, engine, session
    transaction.rollback()
    session.close()
    engine.dispose()
    connection.close()
    db_helper.drop_db()
    TESTING["running"] = False


class MockResponse():
    _json = None

    async def json(self):
        return self._json


class TestDBWriting(unittest.TestCase):
    """Test writing to database."""

    @asynctest.patch("kilogram.slurp.get_the_json")
    @asynctest.patch("kilogram.slurp.fetch")
    def test_weights(self, fetch_mock, get_json_mock):

        with open(FIX_DIR + "/kilogram/fixtures/systems.json") as systems_json:
            system_json = json.loads(systems_json.read())

        with open(FIX_DIR + "/kilogram/fixtures/weigh.json") as weigh_json:
            weigh4_json = json.loads(weigh_json.read())

        with open(FIX_DIR + "/kilogram/fixtures/weigh42.json") as weigh_json:
            weigh42_json = json.loads(weigh_json.read())

        self.assertEqual(slurp.get_start_time(4), (None, None))

        mr = MockResponse()
        mr._json = system_json
        fetch_mock.side_effect = [mr]

        get_json_mock.side_effect = [weigh4_json, weigh42_json]

        slurp.start_import(workers=2, make_engine=False)
        count = session.query(models.KilogramRaw).count()
        self.assertEqual(count, 2)
        self.assertEqual(slurp.get_start_time(4), ('2017-01-01', '10:44:34'))
        copy_to_model.extract_measurements()
        count = session.query(models.KilogramMeasurement).count()
        self.assertEqual(count, 10)
        # check if code is idempotent
        copy_to_model.extract_measurements()
        self.assertEqual(count, 10)
