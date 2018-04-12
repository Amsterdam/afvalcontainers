"""
Some tests.
"""

import json
import time
import unittest
import asynctest
import slurp_api
import models
from settings import BASE_DIR


FIX_DIR = BASE_DIR + '/scrape_api'

transaction = []
connection = []
engine = []
session = []


def setUpModule():
    global transaction, connection, engine, session
    models.create_db()
    engine = models.make_engine(section='test')
    connection = engine.connect()
    transaction = connection.begin()
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = models.set_engine(engine)


def tearDownModule():
    global transaction, connection, engine, session
    transaction.rollback()
    session.close()
    engine.dispose()
    connection.close()
    models.drop_db()


class MockResponse():
    _json = None

    async def json(self):
        return self._json


class TestDBWriting(unittest.TestCase):
    """
    Test writing to database
    """

    @asynctest.patch('slurp_api.get_the_json')
    @asynctest.patch('slurp_api.fetch')
    def test_containers(self, fetch_mock, get_json_mock):

        with open(FIX_DIR + '/fixtures/containers.json') as mockjson:
            test_json = json.loads(mockjson.read())

        items = []
        for item in test_json[:3]:
            items.append(item['container'])

        mr = MockResponse()
        mr._json = {'containers': items}

        get_json_mock.side_effect = test_json[:3]
        fetch_mock.side_effect = [mr]

        slurp_api.start_import('containers', workers=1)
        count = session.query(models.Container).count()
        self.assertEqual(count, 2)

    @asynctest.patch('slurp_api.get_the_json')
    @asynctest.patch('slurp_api.fetch')
    def test_wells(self, get_json_mock, fetch_mock):

        with open(FIX_DIR + '/fixtures/wells.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.side_effect = test_json
        fetch_mock.side_effect = test_json
        slurp_api.start_import('wells', workers=1)
        count = session.query(models.Well).count()
        self.assertEqual(count, 1)

    @asynctest.patch('slurp_api.get_the_json')
    @asynctest.patch('slurp_api.fetch')
    def test_container_types(self, get_json_mock, fetch_mock):

        with open(FIX_DIR + '/fixtures/containertypes.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.side_effect = test_json
        fetch_mock.side_effect = test_json
        slurp_api.start_import('container_types', workers=1)
        count = session.query(models.ContainerType).count()
        self.assertEqual(count, 1)
