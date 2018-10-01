"""
Some tests.
"""

import json
# import time
import unittest
import asynctest
import slurp_bammens
import models
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
    models.create_db()
    engine = models.make_engine(section="test")
    connection = engine.connect()
    transaction = connection.begin()
    session = models.set_session(engine)
    session.execute("CREATE EXTENSION postgis;")
    session.commit()
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


def teardown_module():
    global transaction, connection, engine, session
    transaction.rollback()
    session.close()
    engine.dispose()
    connection.close()
    models.drop_db()
    TESTING["running"] = False


class MockResponse():
    _json = None

    async def json(self):
        return self._json


class TestDBWriting(unittest.TestCase):
    """
    Test writing to database
    """

    @asynctest.patch("slurp_bammens.get_the_json")
    @asynctest.patch("slurp_bammens.fetch")
    def test_containers(self, fetch_mock, get_json_mock):

        with open(FIX_DIR + "/fixtures/containers.json") as detail_json:
            detail_json = json.loads(detail_json.read())

        with open(FIX_DIR + "/fixtures/containers.list.json") as list_json:
            list_json = json.loads(list_json.read())

        mr = MockResponse()
        mr._json = list_json

        get_json_mock.side_effect = detail_json[:6]
        fetch_mock.side_effect = [mr]

        slurp_bammens.start_import("containers", workers=2, make_engine=False)
        count = session.query(models.Container).count()
        self.assertEqual(count, 5)

    @asynctest.patch("slurp_bammens.get_the_json")
    @asynctest.patch("slurp_bammens.fetch")
    def test_wells(self, fetch_mock, get_json_mock):

        with open(FIX_DIR + "/fixtures/wells.json") as detail_json:
            detail_json = json.loads(detail_json.read())

        with open(FIX_DIR + "/fixtures/wells.list.json") as list_json:
            list_json = json.loads(list_json.read())

        mr = MockResponse()
        mr._json = list_json

        get_json_mock.side_effect = detail_json[:4]
        fetch_mock.side_effect = [mr]

        slurp_bammens.start_import("wells", workers=2, make_engine=False)
        count = session.query(models.Well).count()
        self.assertEqual(count, 4)

    @asynctest.patch("slurp_bammens.get_the_json")
    @asynctest.patch("slurp_bammens.fetch")
    def test_container_types(self, fetch_mock, get_json_mock):

        with open(FIX_DIR + "/fixtures/containertypes.json") as detail_json:
            detail_json = json.loads(detail_json.read())

        with open(FIX_DIR + "/fixtures/containertypes.list.json") as list_json:
            list_json = json.loads(list_json.read())

        mr = MockResponse()
        mr._json = list_json

        get_json_mock.side_effect = detail_json[:3]
        fetch_mock.side_effect = [mr]

        slurp_bammens.start_import(
            "container_types", workers=2, make_engine=False)
        count = session.query(models.ContainerType).count()
        self.assertEqual(count, 3)
