from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from datapunt_api.rest import DatapuntViewSet
from datapunt_api.pagination import HALCursorPagination

from django.conf import settings

from enevo.models import EnevoContainer
from enevo.models import EnevoContainerType
from enevo.models import EnevoContainerSlot
from enevo.models import EnevoSite
from enevo.models import EnevoSiteContentType
from enevo.models import EnevoAlert
from enevo.models import EnevoContentType
from enevo.models import EnevoFillLevel

from enevo.serializers import ContainerSerializer
from enevo.serializers import ContainerDetailSerializer
from enevo.serializers import ContainerTypeSerializer
from enevo.serializers import ContainerSlotSerializer
from enevo.serializers import SiteSerializer
from enevo.serializers import SiteDetailSerializer
from enevo.serializers import SiteContentTypeSerializer
from enevo.serializers import AlertSerializer
from enevo.serializers import ContentTypeSerializer
from enevo.serializers import FillLevelSerializer


class ContainerFilter(FilterSet):
    in_bammens = filters.BooleanFilter(
        method='in_bammens_filter', label='in_bammens'
    )

    class Meta(object):
        model = EnevoContainer
        fields = (
            'site_id',
            'site_content_type_id',
            'container_slot_id',
            'container_type_id',
            'customer_key',
            'valid'
        )

    def in_bammens_filter(self, qs, name, value):
        return qs.filter(valid=value)


class ContainerView(DatapuntViewSet):
    queryset = (
        EnevoContainer.objects.all()
        .order_by("id")
    )

    serializer_detail_class = ContainerDetailSerializer
    serializer_class = ContainerSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )
    filter_class = ContainerFilter

    ordering_fields = '__all__'


class ContainerTypeView(DatapuntViewSet):

    queryset = (
        EnevoContainerType.objects.all().order_by('id')
    )
    serializer_detail_class = ContainerTypeSerializer
    serializer_class = ContainerTypeSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['shape', 'has_bag', 'servicing_method', 'volume']
    ordering_fields = '__all__'


class ContainerSlotView(DatapuntViewSet):

    queryset = (
        EnevoContainerSlot.objects.all().order_by('id')
    )
    serializer_detail_class = ContainerSlotSerializer
    serializer_class = ContainerSlotSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = [
        'site_id', 'site_content_type_id',
        'photo',
        # 'container'

    ]

    ordering_fields = '__all__'


FILTERS = ['exact', 'lt', 'gt']


class SiteFilter(FilterSet):
    no_site = filters.BooleanFilter(
        method='in_site_filter', label='in_bammens'
    )

    class Meta(object):
        model = EnevoSite
        fields = {
            'site_id': ['exact'],
            'no_site': ['exact'],
        }

    def in_site_filter(self, qs, name, value):
        return qs.filter(site_id__isnull=not(value))


class SiteView(DatapuntViewSet):

    queryset = (
        EnevoSite.objects.all()
        .order_by('id')
    )
    serializer_detail_class = SiteDetailSerializer
    serializer_class = SiteSerializer
    bbox_filter_field = 'geometrie'

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_class = SiteFilter

    ordering_fields = '__all__'


class SiteContentTypeView(DatapuntViewSet):
    queryset = (
        EnevoSiteContentType.objects.all()
        .order_by('id')
    )
    serializer_detail_class = SiteContentTypeSerializer
    serializer_class = SiteContentTypeSerializer
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['content_type_id', 'site_id']
    ordering_fields = '__all__'


class AlertView(DatapuntViewSet):
    queryset = (
        EnevoAlert.objects.all()
        .order_by('id')
    )
    serializer_detail_class = AlertSerializer
    serializer_class = AlertSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['content_type', 'site']
    ordering_fields = '__all__'


class FillLevelPager(HALCursorPagination):
    """Sidcon pagination configuration.

    Fill-levels will be many. So we use cursor based pagination.
    """
    page_size = 300
    max_page_size = 5000
    ordering = "-id"
    count_table = False


class EnevoPager(HALCursorPagination):
    """Site objects are rather "heavy" so put limits on pagination."""

    page_size = 100
    max_page_size = 9000
    ordering = "-time"
    count_table = False


class FillLevelView(DatapuntViewSet):

    pagination_class = EnevoPager
    serializer_detail_class = FillLevelSerializer
    serializer_class = FillLevelSerializer

    filter_backends = (
        DjangoFilterBackend,
    )

    filter_fields = [
        'content_type',
        'content_type_name',
        'e_site',
        'e_site_name',
        'site_id',
        'frozen',
        'time',
    ]

    def get_queryset(self):
        """
        """
        queryset = (
            EnevoFillLevel.objects.all()
            .order_by("-time")
        )

        if not settings.TESTING:
            queryset = queryset.using('kilogram')

        return queryset


class ContentTypeView(DatapuntViewSet):
    queryset = (
        EnevoContentType.objects.all()
        .order_by('id')
    )
    serializer_detail_class = ContentTypeSerializer
    serializer_class = ContentTypeSerializer

    ordering_fields = '__all__'
