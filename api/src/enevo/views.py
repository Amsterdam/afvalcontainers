from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from datapunt_api.rest import DatapuntViewSet
from enevo.models import EnevoContainer
from enevo.models import EnevoContainerType
from enevo.models import EnevoContainerSlot
from enevo.models import EnevoSite
from enevo.models import EnevoSiteContentType
from enevo.models import EnevoAlert
from enevo.models import EnevoContentType


from enevo.serializers import ContainerSerializer
from enevo.serializers import ContainerDetailSerializer
from enevo.serializers import ContainerTypeSerializer
from enevo.serializers import ContainerSlotSerializer
from enevo.serializers import SiteSerializer
from enevo.serializers import SiteDetailSerializer
from enevo.serializers import SiteContentTypeSerializer
from enevo.serializers import AlertSerializer
from enevo.serializers import ContentTypeSerializer


class ContainerFilter(FilterSet):
    in_bammens = filters.BooleanFilter(
        method='in_bammens_filter', label='in_bammens'
    )

    class Meta(object):
        model = EnevoContainer
        fields = (
            'site',
            'site_content_type',
            'container_slot',
            'container_type',
            'customer_key',
            'valid'
        )

    def in_bammens_filter(self, qs, name, value):
        return qs.filter(valid=value)


class ContainerView(DatapuntViewSet):
    queryset = (
        EnevoContainer.objects.all()
        .order_by("id")
        .select_related('site', 'site_content_type',
                        'container_slot')
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
        EnevoContainerType.objects.all()
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
        EnevoContainerSlot.objects.all()
    )
    serializer_detail_class = ContainerSlotSerializer
    serializer_class = ContainerSlotSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['site', 'site_content_type', 'photo', 'container']

    ordering_fields = '__all__'


class SiteView(DatapuntViewSet):

    queryset = (
        EnevoSite.objects.all()
    )
    serializer_detail_class = SiteDetailSerializer
    serializer_class = SiteSerializer
    bbox_filter_field = 'geometrie'

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['photo']

    ordering_fields = '__all__'


class SiteContentTypeView(DatapuntViewSet):
    queryset = (
        EnevoSiteContentType.objects.all()
    )
    serializer_detail_class = SiteContentTypeSerializer
    serializer_class = SiteContentTypeSerializer
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['content_type', 'site']
    ordering_fields = '__all__'


class AlertView(DatapuntViewSet):
    queryset = (
        EnevoAlert.objects.all()
    )
    serializer_detail_class = AlertSerializer
    serializer_class = AlertSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['content_type', 'site']
    ordering_fields = '__all__'


class ContentTypeView(DatapuntViewSet):
    queryset = (
        EnevoContentType.objects.all()
    )
    serializer_detail_class = ContentTypeSerializer
    serializer_class = ContentTypeSerializer

    ordering_fields = '__all__'
