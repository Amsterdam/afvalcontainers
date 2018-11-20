"""Some enevo.com tests."""

import json
# import time
import unittest
import asynctest
from enevo import slurp
from enevo import models

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

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_fill_levels(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/fill_levels.json") as fill_levels:
            fill_levels_json = json.loads(fill_levels.read())

        mr = MockResponse()
        mr._json = fill_levels_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='fill_levels', make_engine=False)
        count = session.query(models.EnevoFillLevel).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='fill_levels', make_engine=False)
        count = session.query(models.EnevoFillLevel).count()
        self.assertEqual(count, 4)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_containers(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/containers.json") as containers:
            containers_json = json.loads(containers.read())

        mr = MockResponse()
        mr._json = containers_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='containers', make_engine=False)
        count = session.query(models.EnevoContainer).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='containers', make_engine=False)
        count = session.query(models.EnevoContainer).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_sites(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/sites.json") as sites:
            sites_json = json.loads(sites.read())

        mr = MockResponse()
        mr._json = sites_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='sites', make_engine=False)
        count = session.query(models.EnevoSite).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='sites', make_engine=False)
        count = session.query(models.EnevoContainer).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_alerts(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/alerts.json") as alerts:
            alerts_json = json.loads(alerts.read())

        mr = MockResponse()
        mr._json = alerts_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='alerts', make_engine=False)
        count = session.query(models.EnevoAlert).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='alerts', make_engine=False)
        count = session.query(models.EnevoAlert).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_container_types(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/container_types.json") as container_types:
            container_types_json = json.loads(container_types.read())

        mr = MockResponse()
        mr._json = container_types_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='container_types', make_engine=False)
        count = session.query(models.EnevoContainerType).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='container_types', make_engine=False)
        count = session.query(models.EnevoContainerType).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_container_slots(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/container_slots.json") as container_slots:
            container_slots_json = json.loads(container_slots.read())

        mr = MockResponse()
        mr._json = container_slots_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='container_slots', make_engine=False)
        count = session.query(models.EnevoContainerSlot).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='container_slots', make_engine=False)
        count = session.query(models.EnevoContainerSlot).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_site_content_types(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/site_content_types.json") as site_content_types:
            site_content_types_json = json.loads(site_content_types.read())

        mr = MockResponse()
        mr._json = site_content_types_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='site_content_types', make_engine=False)
        count = session.query(models.EnevoSiteContentType).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='site_content_types', make_engine=False)
        count = session.query(models.EnevoSiteContentType).count()
        self.assertEqual(count, 2)

    @asynctest.patch("enevo.slurp.get_session_token")
    @asynctest.patch("enevo.slurp.fetch")
    def test_import_content_types(self, fetch_mock, get_token_mock):
        with open(FIX_DIR + "/enevo/fixtures/content_types.json") as content_types:
            content_types_json = json.loads(content_types.read())

        mr = MockResponse()
        mr._json = content_types_json
        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='content_types', make_engine=False)
        count = session.query(models.EnevoContentType).count()
        self.assertEqual(count, 2)

        fetch_mock.side_effect = [mr]
        get_token_mock.side_effect = ['test_token']

        slurp.start_import(endpoint='content_types', make_engine=False)
        count = session.query(models.EnevoContentType).count()
        self.assertEqual(count, 2)
