# Packages
from rest_framework.test import APITestCase

from . import factories


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        'parkeervakken/parkeervakken',
        'parkeervakken/geosearch',
        'parkeervakken/geoselection',
    ]

    with_count = [
        'parkeervakken/parkeervakken',
    ]

    def setUp(self):

        self.p = factories.ParkeervakFactory()

    def valid_html_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'text/html; charset=utf-8', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_index_pages(self):
        url = 'parkeervakken'

        response = self.client.get('/{}/'.format(url))

        self.assertEqual(
            response.status_code,
            200, 'Wrong response code for {}'.format(url))

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.assertEqual(
                response.status_code,
                200, 'Wrong response code for {}'.format(url))

            self.assertEqual(
                response['Content-Type'], 'application/json',
                'Wrong Content-Type for {}'.format(url))

            if url in self.with_count:
                self.assertIn(
                    'count', response.data,
                    'No count attribute in {}'.format(url))

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            if url in self.with_count:
                self.assertIn(
                    'count',
                    response.data,
                    'No count attribute in {}'.format(url))
