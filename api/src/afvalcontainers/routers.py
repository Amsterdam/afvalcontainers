from django.urls import reverse
from rest_framework import routers

from afvalcontainers import API_VERSIONS
from afvalcontainers import get_version


class AfvalContainerAPIRootView(routers.APIRootView):
    """
    Garbadge Containers in the city are show here as list.

    It is possible to filter the list

    Model Overview
    ==================

    Type ->  Container ->  Well ->  Site

    A site is a collection of wells. Each well can contain
    a container. The container and type in a well can change.

    Daily Import Overview
    =====================

     1. Scrape Bammens API ~12.500 wells/containers
     2. BGT merge ~8500 wells merged with BGT (8-2018)
     3. Cleanup ,
     4. Fills site endpoint for route planning/ dashboards
     5. Publish API / Geo services

    [github/amsterdam/afvalcontainers](https://github.com/Amsterdam/afvalcontainers)

    Continues Import Overview
    =========================

    A few suppliers provide real-time data.

    kilogram.nl for live weigh measurements.
    sidcon for live feed  sidcon (rest) containers.
    enevo live feed filling plastic containers.

    All measurements will or are coupled to a site.

    [Author: s.preeker](https://github.com/spreeker/)


    """
    def get_view_name(self):
        return 'AfvalContainers API'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        v1_root = reverse('v1:api-root')
        supply_root = reverse('suppliers:api-root')

        # Appending the index view with API version 1 information.
        response.data['v1'] = {
            '_links': {
                'self': {
                    'href': request._request.build_absolute_uri(v1_root),
                }
            },
            'version': get_version(API_VERSIONS['v1']),
            'status': 'Official endpoint, will be stable',
        }

        response.data['suppliers'] = {
            '_links': {
                'self': {
                    'href': request._request.build_absolute_uri(supply_root),
                }
            },
            'status': 'Can change any time.',
        }

        return response


class SupliersAPIRootView(routers.APIRootView):
    """Suplier data API. Used to inspect suplier data.

    no garantees are given on this API since supliers can change over time.

    Here you can check, validate, all different suppliers data.
    """

    def get_view_name(self):
        return 'Data suppliers APIs'
