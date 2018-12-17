# Packages
import datetime
import pytz

from rest_framework.test import APITestCase

from sidcon.tests import factories as sidconfactory

# import logging

# LOG = logging.getLogger(__name__)


class SidconActionTestCase(APITestCase):

    urls_counts = [
        ("afval/sidcon/filllevels/latest", 3),
        ("afval/sidcon/filllevels/today_full", 1),
    ]

    def valid_response(self, url, response, content_type):
        """Check common status/json."""
        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

        self.assertEqual(
            f"{content_type}",
            response["Content-Type"],
            "Wrong Content-Type for {}".format(url),
        )

    def setUp(self):

        self.sidcon1 = sidconfactory.SidconFillLevelFactory(
            valid=False,
            scraped_at=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        )
        self.sidcon1.valid = True
        self.sidcon1.save()

        day1 = datetime.timedelta(days=1)
        yesterday = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - day1
        self.sidcon2 = sidconfactory.SidconFillLevelFactory()
        self.sidcon2.scraped_at = yesterday
        self.sidcon2.save()

        self.sidcon3 = sidconfactory.SidconFillLevelFactory(
            valid=False,
            scraped_at=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC),
            communication_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC),
            filling=100
        )
        self.sidcon3.valid = True
        self.sidcon3.save()

    def test_lists(self):
        for url, count in self.urls_counts:
            response = self.client.get("/{}/".format(url))
            # default should be json
            self.valid_response(url, response, 'application/json')

            self.assertEqual(len(response.data), count)

    # TODO test filters fields etc
