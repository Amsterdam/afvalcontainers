import json
# import time
import unittest
from unittest import mock
# import asynctest
from sidcon import slurp_sidcon
from sidcon import models

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
    """Request Session object mocked

    Gives fixtures as response.
    """
    _json_fill = None
    _json_containers = None

    _response_data = None

    status_code = 200

    def json(self):
        return self._response_data

    def post(self, url, data={}, json={}):
        self._response_data = self._json_fill
        return self

    def get(self, url, params={}):
        self._response_data = self._json_containers
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class TestDBWriting(unittest.TestCase):
    """Test writing to database."""

    @mock.patch("requests.Session")
    def test_import_fill_levels(self, fetch_mock):
        with open(FIX_DIR + "/sidcon/fixtures/response.json") as fill_levels:
            fill_levels_json = json.loads(fill_levels.read())

        with open(FIX_DIR + "/sidcon/fixtures/containers.json") as fill_levels:
            containers_json = json.loads(fill_levels.read())

        mr = MockResponse()
        mr._json_fill = fill_levels_json
        mr._json_containers = containers_json
        fetch_mock.side_effect = [mr, mr]

        slurp_sidcon.get_sidcon_container_status()
        slurp_sidcon.store_container_status_in_api()

        count = session.query(models.SidconFillLevel).count()
        self.assertEqual(count, 241)

        # test idempotency
        # slurp_sidcon.store_container_status_in_api()
        count = session.query(models.SidconFillLevel).count()
        self.assertEqual(count, 241)

        # test validation
        db_model = models.SidconFillLevel
        count = (
            session.query(db_model)
            .filter(db_model.valid.is_(True))
            .count()
        )
        self.assertEqual(count, 4)
