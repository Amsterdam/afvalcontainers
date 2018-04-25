from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import ValidationError
from django.contrib.gis.geos import Polygon
from django.contrib.gis.measure import Distance

from datapunt_api.rest import DatapuntViewSet
from datapunt_api import bbox

from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType
from afvalcontainers.models import Buurten
from afvalcontainers.serializers import ContainerSerializer
from afvalcontainers.serializers import WellSerializer
from afvalcontainers.serializers import TypeSerializer


WASTE_DESCRIPTIONS = (
    ("Rest"),
    ("Glas"),
    ("Glas"),
    ("Papier"),
    ("Textiel"),
    ("Wormen"),
    ("Glas"),
    ("Plastic"),
    ("Blipvert"),
)

STADSDELEN = (
    ("B", "Westpoort (B)"),
    ("M", "Oost (M)"),
    ("N", "Noord (N)"),
    ("A", "Centrum (A)"),
    ("E", "West (E)"),
    ("F", "Nieuw-West (F)"),
    ("K", "Zuid (K)"),
    ("T", "Zuidoost (T)"),
)

WASTE_CHOICES = [(w, w) for w in WASTE_DESCRIPTIONS]


def buurt_choices():
    options = Buurten.objects.values_list('vollcode', 'naam')
    return [(c, '%s (%s)' % (n, c)) for c, n in options]


class ContainerFilter(FilterSet):
    id = filters.CharFilter()
    in_bbox = filters.CharFilter(method='in_bbox_filter', label='bbox')
    no_well = filters.BooleanFilter(method='no_well_filter', label='no_well')
    location = filters.CharFilter(
            method="locatie_filter", label='x,y,r')

    waste_name = filters.ChoiceFilter(
        choices=WASTE_CHOICES, label='waste name')
    well__stadsdeel = filters.ChoiceFilter(choices=STADSDELEN)
    well__buurt_code = filters.ChoiceFilter(choices=buurt_choices)

    class Meta(object):
        model = Container
        fields = (
            "id",
            "id_number",
            "serial_number",
            "active",
            "waste_type",
            "waste_name",
            "placing_date",
            "operational_date",
            "warranty_date",
            "well__buurt_code",
            "well__stadsdeel",
            "well",
            "no_well",
            "container_type",
            "in_bbox",
            "location",
        )

    def in_bbox_filter(self, qs, name, value):
        bbox_values, err = bbox.valid_bbox(value)
        lat1, lon1, lat2, lon2 = bbox_values
        poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        if err:
            raise ValidationError(f"bbox invalid {err}:{bbox_values}")
        return qs.filter(well__geometrie__bboverlaps=(poly_bbox))

    def no_well_filter(self, qs, name, value):
        return qs.filter(well=None)

    def locatie_filter(self, qs, name, value):
        point, radius = bbox.parse_xyr(value)
        return qs.filter(
            well__geometrie__dwithin=(point, radius))


class ContainerView(DatapuntViewSet):
    """View of Containers.
    """
    queryset = (
        Container.objects.all()
        .order_by("id")
        .select_related('well')
        .select_related('container_type')
    )
    serializer_detail_class = ContainerSerializer
    serializer_class = ContainerSerializer
    bbox_filter_field = 'well__geometrie'
    filter_backends = (DjangoFilterBackend,)
    filter_class = ContainerFilter


class WellFilter(FilterSet):
    id = filters.CharFilter()
    in_bbox = filters.CharFilter(method='in_bbox_filter', label='bbox')
    no_container = filters.BooleanFilter(
        method='no_container_filter', label='no_container')

    location = filters.CharFilter(
        method="locatie_filter", label='x,y,r')

    stadsdeel = filters.ChoiceFilter(choices=STADSDELEN)
    buurt_code = filters.ChoiceFilter(choices=buurt_choices)

    class Meta(object):
        model = Well
        fields = (
            "id",
            "id_number",
            "serial_number",
            "buurt_code",
            "stadsdeel",
            "created_at",
            "placing_date",
            "operational_date",
            "warranty_date",
            "containers",
            "in_bbox",
            "location",
            "no_container",
        )

    def locatie_filter(self, qs, name, value):
        point, radius = bbox.parse_xyr(value)
        return qs.filter(geometrie__dwithin=(point, radius))

    def in_bbox_filter(self, qs, name, value):
        bbox_values, err = bbox.valid_bbox(value)
        lat1, lon1, lat2, lon2 = bbox_values
        poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        if err:
            raise ValidationError(f"bbox invalid {err}:{bbox_values}")
        return qs.filter(geometrie__bboverlaps=(poly_bbox))

    def no_container_filter(self, qs, name, value):
        return qs.filter(containers=None)


class WellView(DatapuntViewSet):
    """View of Wells.
    """
    queryset = (
        Well.objects.all()
        .order_by("id")
        .prefetch_related('containers')
    )
    serializer_detail_class = WellSerializer
    serializer_class = WellSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = WellFilter


class TypeView(DatapuntViewSet):
    """View of Types.
    """
    queryset = ContainerType.objects.all().order_by("id")
    serializer_detail_class = TypeSerializer
    serializer_class = TypeSerializer
    filter_backends = (DjangoFilterBackend,)
