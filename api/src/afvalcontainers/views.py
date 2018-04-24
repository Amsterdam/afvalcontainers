from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from datapunt_api.rest import DatapuntViewSet

from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType
from afvalcontainers.serializers import ContainerSerializer
from afvalcontainers.serializers import WellSerializer
from afvalcontainers.serializers import TypeSerializer


class ContainerFilter(FilterSet):
    id = filters.CharFilter()

    class Meta(object):
        model = Container
        fields = (
            "id",
            "id_number",
            "serial_number",
            "active",
            "waste_type",
            "placing_date",
            "operational_date",
            "warranty_date",
            # 'buurtcode',
            # 'stadsdeel',
            # 'straatnaam',
            # 'soort',
            "well__buurt_code",
            "well__stadsdeel",
            "well",
            "container_type",
        )


class ContainerList(DatapuntViewSet):
    """View of Containers.
    """
    queryset = Container.objects.all().order_by("id")
    serializer_detail_class = ContainerSerializer
    serializer_class = ContainerSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ContainerFilter
    queryset_detail = (Container.objects.all())


class WellFilter(FilterSet):
    id = filters.CharFilter()

    class Meta(object):
        model = Well
        fields = (
            "id",
            "id_number",
            "serial_number",
            "buurt_code",
            "created_at",
            "placing_date",
            "operational_date",
            "warranty_date",
            "containers",
        )


class WellList(DatapuntViewSet):
    """View of Wells.
    """
    queryset = Well.objects.all().order_by("id")
    serializer_detail_class = WellSerializer
    serializer_class = WellSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = WellFilter
    queryset_detail = (Well.objects.all())


class TypeList(DatapuntViewSet):
    """View of Types.
    """
    queryset = ContainerType.objects.all().order_by("id")
    serializer_detail_class = TypeSerializer
    serializer_class = TypeSerializer
    filter_backends = (DjangoFilterBackend,)
    queryset_detail = (ContainerType.objects.all())
