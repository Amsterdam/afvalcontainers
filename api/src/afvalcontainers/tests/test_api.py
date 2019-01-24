# Packages
import datetime
import pytz

from rest_framework.test import APITestCase

from . import factories
from kilogram.tests import factories as kilofactory
from enevo.tests import factories as enevofactory
from sidcon.tests import factories as sidconfactory

# import logging

# LOG = logging.getLogger(__name__)


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        "afval/v1/containers",
        "afval/v1/wells",
        "afval/v1/containertypes",
        "afval/v1/sites",

        # "afval/kilogram",
        # "afval/kilos/neighborhood/weekly",
        # "afval/kilos/sites/weekly",
        # "afval/kilos/neighborhood/monthly",
        # "afval/kilos/sites/monthly",

        "afval/suppliers/enevo/containers",
        "afval/suppliers/enevo/containertypes",
        "afval/suppliers/enevo/containerslots",
        "afval/suppliers/enevo/sites",
        "afval/suppliers/enevo/sitecontenttypes",
        "afval/suppliers/enevo/alerts",
        "afval/suppliers/enevo/filllevels",

        "afval/suppliers/sidcon/filllevels",
    ]

    def setUp(self):
        self.t = factories.ContainerTypeFactory()
        self.w = factories.WellFactory()
        self.c = factories.ContainerFactory(
            container_type=self.t,
            well=self.w
        )
        self.s = factories.SiteFactory()
        self.w.site_id = self.s.id
        self.w.save()
        self.snull = factories.SiteFactory()
        self.snull.short_id = None
        self.snull.save()

        self.k = kilofactory.KiloFactory()
        self.k.site_id = self.s.id
        self.k.container_id = self.c.id
        self.k.save()

        kilofactory.make_stats_values(self.s)

        self.es = enevofactory.SiteFactory()
        self.et = enevofactory.ContentTypeFactory()
        self.ect = enevofactory.ContainerTypeFactory()
        self.ea = enevofactory.AlertFactory(site=self.es)

        self.est = enevofactory.SiteContentTypeFactory()
        self.est.site = self.es
        self.est.content_type = self.et
        self.est.save()

        self.ecs = enevofactory.ContainerSlotFactory()
        self.ecs.site = self.es
        self.ecs.content_type = self.et
        self.ecs.site_content_type = self.est
        self.ecs.save()

        self.ec = enevofactory.ContainerFactory()
        self.ec.site = self.es
        self.ec.site_content_type = self.est
        self.ec.container_slot = self.ecs
        self.ec.container_type = self.ect
        self.ec.valid = True
        self.ec.save()

        self.e_fill_level = enevofactory.FillLevelFactory()

        self.sidcon1 = sidconfactory.SidconFillLevelFactory(
            valid=False,
            scraped_at=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        )
        day1 = datetime.timedelta(days=1)
        self.sidcon1.valid = True
        self.sidcon1.save()

        yesterday = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - day1
        self.sidcon2 = sidconfactory.SidconFillLevelFactory()
        self.sidcon2.scraped_at = yesterday
        self.sidcon2.save()

    def test_openapi(self):
        """Check if we can get openapi json."""
        url = "/afval/swagger/"
        response = self.client.get(url, {'format': 'openapi'})
        self.valid_response(
            url, response, 'application/openapi+json; charset=utf-8')

    def valid_response(self, url, response, content_type):
        """Check common status/json."""
        self.assertEqual(
            200, response.status_code,
            "Wrong response code for {}".format(url),
        )

        self.assertEqual(
            f"{content_type}",
            response.get("Content-Type"),
            "Wrong Content-Type for {}".format(url),
        )

    def test_index_pages(self):
        url = "afval"

        response = self.client.get("/{}/".format(url))

        self.assertEqual(
            response.status_code, 200, "Wrong response code for {}".format(url)
        )

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get("/{}/".format(url))

            self.assertEqual(
                response.status_code, 200,
                "Wrong response code for {}".format(url)
            )

            # default should be json
            self.valid_response(url, response, 'application/json')

            self.assertEqual(
                response["Content-Type"],
                "application/json",
                "Wrong Content-Type for {}".format(url),
            )

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=api".format(url))

            self.valid_response(url, response, 'text/html; charset=utf-8')

    def test_lists_csv(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=csv".format(url))

            self.valid_response(url, response, 'text/csv; charset=utf-8')

    def test_lists_xml(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=xml".format(url))

            self.valid_response(
                url, response, 'application/xml; charset=utf-8')

    def test_site_filters(self):
        url = "afval/v1/sites"
        response = self.client.get(f"/{url}/", {'short_id': self.s.short_id})
        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(int(response.data['results'][0]['id']), self.s.id)

    def test_site_null_filter(self):
        url = "afval/v1/sites"
        response = self.client.get(f"/{url}/", {'no_short_id': 1})
        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(int(response.data['results'][0]['id']), self.snull.id)

    def test_enevo_container_in_bammens_filter_true(self):
        url = "afval/suppliers/enevo/containers"
        response = self.client.get(f"/{url}/", {'in_bammens': True})
        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(int(response.data['results'][0]['id']), self.ec.id)

        response = self.client.get(f"/{url}/", {'in_bammens': False})
        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 0)

    def test_enevo_container_in_bammens_filter_false(self):
        url = "afval/suppliers/enevo/containers"
        response = self.client.get(f"/{url}/", {'in_bammens': True})
        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(int(response.data['results'][0]['id']), self.ec.id)

        enevofactory.ContainerFactory.create_batch(3, valid=False)

        response = self.client.get(f"/{url}/", {'in_bammens': False})

        self.valid_response(url, response, 'application/json')
        self.assertEqual(response.data['count'], 3)
