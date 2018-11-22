from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import ValidationError
from django.contrib.gis.geos import Polygon
from django.conf import settings
# from django.contrib.gis.measure import Distance

from datapunt_api.rest import DatapuntViewSet
from datapunt_api.pagination import HALPagination
from datapunt_api import bbox

from enevo.models import EnevoContainer
from enevo.models import EnevoContainerType
from enevo.models import EnevoContainerSlot
from enevo.models import EnevoSite
from enevo.models import EnevoSiteContentType
from enevo.models import EnevoAlert
from enevo.models import EnevoContentType

# Move into new app?

from enevo.serializers import ContainerSerializer
from enevo.serializers import ContainerDetailSerializer
from enevo.serializers import ContainerTypeSerializer
from enevo.serializers import ContainerSlotSerializer
from enevo.serializers import SiteSerializer
from enevo.serializers import SiteDetailSerializer
from enevo.serializers import SiteContentTypeSerializer
from enevo.serializers import AlertSerializer
from enevo.serializers import ContentTypeSerializer


class ContainerView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

    queryset = (
        EnevoContainer.objects.all()
        .order_by("id")
        .select_related('site', 'site_content_type',
                        'container_slot')
    )
    serializer_detail_class = ContainerDetailSerializer
    serializer_class = ContainerSerializer
    #bbox_filter_field = 'well__geometrie'

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['site', 'site_content_type', 'container_slot', 'container_type', 'customer_key']

    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class ContainerTypeView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

    queryset = (
        EnevoContainerType.objects.all()
    )
    serializer_detail_class = ContainerTypeSerializer
    serializer_class = ContainerTypeSerializer
    #bbox_filter_field = 'well__geometrie'

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = ['shape', 'has_bag', 'servicing_method', 'volume']

    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class ContainerSlotView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

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

    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class SiteView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

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

    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class SiteContentTypeView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

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
    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class AlertView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

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
    ##filter_class = ContainerFilter
    ordering_fields = '__all__'


class ContentTypeView(DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is a legacy number
    """

    queryset = (
        EnevoContentType.objects.all()
    )
    serializer_detail_class = ContentTypeSerializer
    serializer_class = ContentTypeSerializer

    ordering_fields = '__all__'
