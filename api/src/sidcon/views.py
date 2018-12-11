
from django.conf import settings
from datapunt_api.rest import DatapuntViewSet
# from datapunt_api.pagination import HALPagination
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import FilterSet

from sidcon.models import SidconFillLevel
from sidcon.serializers import SidconSerializer
from sidcon.serializers import SidconDetailSerializer

from rest_framework.pagination import CursorPagination

FILTERS = ['exact', 'lt', 'gt']


class SidconPager(CursorPagination):
    """Site objects are rather "heavy" so put limits on pagination."""

    page_size = 100
    max_page_size = 1000
    ordering = "-id"


class SidconFilter(FilterSet):
    """Filtering on sidcon fill level entries."""

    class Meta(object):
        model = SidconFillLevel

        fields = {
            "scraped_at": FILTERS,
            "filling": FILTERS,
            "container_id": FILTERS,
        }


class SidconView(DatapuntViewSet):
    """View of SIDCON container fill level measurements.

    source: https://sidconpers2.mic-o-data.nl

    extract all examples measurements:

    https://api.data.amsterdam.nl/afval/kilogram/?page_size=100

    parameter ?detailed=1  Will give you geometry and extra information

    """

    serializer_class = SidconSerializer
    serializer_detail_class = SidconDetailSerializer
    bbox_filter_field = 'geometrie'
    filter_backends = (DjangoFilterBackend)
    filter_class = SidconFilter
    pagination_class = SidconPager
    ordering_fields = '__all__'

    def get_queryset(self):
        """By default use kilogram database.

        EXCEPT when testing
        """
        queryset = (
            SidconFillLevel.objects.all()
            .order_by("-scraped_at")
        )
        if not settings.TESTING:
            queryset = queryset.using('kilogram')

        return queryset
