
import datetime
import pytz

from django.conf import settings
from datapunt_api.rest import DatapuntViewSet
from datapunt_api.pagination import HALCursorPagination
# from datapunt_api.pagination import HALPagination
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import filters
from django_filters.rest_framework import FilterSet
from rest_framework.decorators import action
from rest_framework.response import Response

from sidcon.models import SidconFillLevel
from sidcon.serializers import SidconSerializer
from sidcon.serializers import SidconDetailSerializer

# from rest_framework.pagination import CursorPagination

from rest_flex_fields.views import FlexFieldsMixin


FILTERS = ['exact', 'lt', 'gt']


class SidconPager(HALCursorPagination):
    """Sidcon pagination configuration.

    Fill-levels will be many. So we use cursor based pagination.
    """

    page_size = 100
    max_page_size = 5000
    ordering = "-id"
    count_table = False


class SidconFilter(FilterSet):
    """Filtering on sidcon fill level entries."""

    container_id = filters.CharFilter(
        method='container_filter', label='container id')

    site_id = filters.CharFilter(
        method='site_filter', label='short site id')

    days_back = filters.NumberFilter(
        method='delta_day_filter', label='days back')

    class Meta(object):
        model = SidconFillLevel

        fields = {
            "scraped_at": FILTERS,
            "filling": FILTERS,
            "communication_date_time": FILTERS,
            "container_id": ['exact'],
            "days_back": ['exact'],
            "valid": ['exact'],
            "short_id": ['exact'],
            "site_id": ['exact'],
        }

    def container_filter(self, qs, name, value):
        return qs.filter(description=value)

    def site_filter(self, qs, name, value):
        return qs.filter(site_id=value)

    def delta_day_filter(self, qs, name, value):
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=int(value))
        filter_day = today - delta
        return qs.filter(communication_date_time__gt=filter_day)


class SidconView(FlexFieldsMixin, DatapuntViewSet):
    """View of SIDCON container fill level measurements.

    source: https://sidconpers2.mic-o-data.nl

    extract all examples measurements:

    parameter ?detailed=1  Will give you geometry and extra information

    show all available fields

    [/afval/suppliers/sidcon/filllevels/?detailed=1](https://api.data.amsterdam.nl/afval/suppliers/sidcon/filllevels/?detailed=1)

    use fields parameter to filter fields

    [/afval/suppliers/sidcon/filllevels/?detailed=1&fields=scraped_at,valid](https://api.data.amsterdam.nl/afval/suppliers/sidcon/filllevels/?detailed=1&fields=scraped_at,valid)

    *checkout the extra action views above*
    """

    serializer_class = SidconSerializer
    serializer_detail_class = SidconDetailSerializer
    bbox_filter_field = 'geometrie'
    filter_backends = (
        DjangoFilterBackend,
        # OrderingFilter
    )
    filter_class = SidconFilter
    pagination_class = SidconPager
    ordering_fields = '__all__'

    def get_queryset(self):
        """By default use kilogram database.

        EXCEPT when testing
        """
        queryset = (
            SidconFillLevel.objects.all()
            .order_by("-id")
        )

        if not settings.TESTING:
            queryset = queryset.using('kilogram')

        return queryset

    @action(detail=False)
    def today_full(self, request):
        """Show containers that have a filling of more then 90 for today."""
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        filter_day = today - delta
        filter_day = filter_day.replace(tzinfo=pytz.UTC)
        qs = self.get_queryset()

        qs = (
            qs.filter(filling__gt=90)
            .filter(communication_date_time__gt=filter_day)
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def latest(self, request):
        """Return the latest scraped data.

        Returns distinct container id's scraped in the last hour.
        """
        today = datetime.datetime.now()
        delta = datetime.timedelta(hours=1)
        filter_day = today - delta
        filter_day = filter_day.replace(tzinfo=pytz.UTC)

        qs = self.get_queryset()
        qs = (
            qs.order_by('-scraped_at', 'description')
            .filter(communication_date_time__gt=filter_day)
            .distinct('scraped_at', 'description')
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def invalid_container_id(self, request):
        today = datetime.datetime.now()
        delta = datetime.timedelta(hours=1)
        filter_day = today - delta
        filter_day = filter_day.replace(tzinfo=pytz.UTC)

        qs = self.get_queryset()
        qs = (
            qs.order_by('-scraped_at', 'description')
            .distinct('scraped_at', 'description')
            .filter(valid=False)
            .filter(communication_date_time__gt=filter_day)
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
