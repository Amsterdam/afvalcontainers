# Packages
from rest_framework.test import APITestCase

from . import factories


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        "afval/containers",
        "afval/wells",
        "afval/containertypes",
    ]

    def setUp(self):
        self.t = factories.ContainerTypeFactory()
        self.w = factories.WellFactory()
        self.c = factories.ContainerFactory(
            container_type=self.t,
            well=self.w
        )

    def valid_response(self, url, response, content_type):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

        self.assertEqual(
            f"{content_type}",
            response["Content-Type"],
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

            self.assertIn(
                "count", response.data, "No count attribute in {}".format(url)
            )

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=api".format(url))

            self.valid_response(url, response, 'text/html; charset=utf-8')

            self.assertIn(
                "count", response.data, "No count attribute in {}".format(url)
            )

    def test_lists_csv(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=csv".format(url))

            self.valid_response(url, response, 'text/csv; charset=utf-8')

            self.assertIn(
                "count", response.data, "No count attribute in {}".format(url)
            )

    def test_lists_xml(self):
        for url in self.datasets:
            response = self.client.get("/{}/?format=xml".format(url))

            self.valid_response(
                url, response, 'application/xml; charset=utf-8')

            self.assertIn(
                "count", response.data, "No count attribute in {}".format(url)
            )
