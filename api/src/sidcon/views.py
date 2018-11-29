
from django.conf import settings
from datapunt_api.rest import DatapuntViewSet
from datapunt_api.pagination import HALPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import FilterSet

from sidcon.models import SidconFillLevel

FILTERS = ['exact', 'lt', 'gt']


class SidconPager(HALPagination):
    """Site objects are rather "heavy" so put limits on pagination."""

    page_size = 100
    max_page_size = 9000


class SidconFilter(FilterSet):
    """wip"""
    pass



class SidconView(DatapuntViewSet):
    """View of container weigh measurements.

    source: kilogram.nl

    extract all examples measurements:

    https://api.data.amsterdam.nl/afval/kilogram/?page_size=100

    parameter ?detailed=1  Will give you geometry and extra information

    """

    serializer_class = SidconSerializer
    serializer_detail_class = SidconDetailSerializer
    bbox_filter_field = 'geometrie'
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = SidconFilter
    ordering_fields = '__all__'

    def get_queryset(self):
        """
        """
        queryset = (
            SidconFillLevel.objects.all()
            .order_by("-scraped_at")
        )
        if not settings.TESTING:
            queryset = queryset.using('kilogram')

        return queryset


