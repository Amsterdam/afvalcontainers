from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import ValidationError
from django.contrib.gis.geos import Polygon
from django.conf import settings
# from django.contrib.gis.measure import Distance

from rest_flex_fields.views import FlexFieldsMixin

from datapunt_api.rest import DatapuntViewSet
from datapunt_api.pagination import HALPagination
from datapunt_api import bbox

from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType
from afvalcontainers.models import Buurten
from afvalcontainers.models import Site
from afvalcontainers.models import SiteFractie

# Move into new app?

from afvalcontainers.serializers import ContainerSerializer
from afvalcontainers.serializers import ContainerDetailSerializer
from afvalcontainers.serializers import WellSerializer
from afvalcontainers.serializers import TypeSerializer
from afvalcontainers.serializers import SiteSerializer
from afvalcontainers.serializers import SiteDetailSerializer
from afvalcontainers.serializers import SiteFractieSerializer
from afvalcontainers.serializers import SiteFractieDetailSerializer


def buurt_choices():
    options = Buurten.objects.values_list('vollcode', 'naam')
    return [(c, '%s (%s)' % (n, c)) for c, n in options]


class ContainerFilter(FilterSet):
    id = filters.CharFilter()
    in_bbox = filters.CharFilter(method='in_bbox_filter', label='bbox')
    no_well = filters.BooleanFilter(method='no_well_filter', label='no_well')
    no_site = filters.BooleanFilter(method='no_site_filter', label='no_site')

    location = filters.CharFilter(
        method="locatie_filter", label='x,y,r')

    waste_name = filters.ChoiceFilter(
        choices=settings.WASTE_CHOICES, label='waste name')
    well__stadsdeel = filters.ChoiceFilter(choices=settings.STADSDELEN)
    well__buurt_code = filters.ChoiceFilter(choices=buurt_choices)

    well = filters.CharFilter()

    detailed = filters.BooleanFilter(
        method='detailed_filter', label='detailed')

    def detailed_filter(self, qs, name, value):
        """Do nothing trigger detailed serializer."""
        return qs

    class Meta(object):
        model = Container
        fields = (
            "detailed",
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
            "container_type__volume",
            "container_type__weight",
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

    def no_site_filter(self, qs, name, value):
        return qs.filter(well__site=None)

    def locatie_filter(self, qs, name, value):
        point, radius = bbox.parse_xyr(value)
        return qs.filter(
            well__geometrie__dwithin=(point, radius))


class ContainerView(FlexFieldsMixin, DatapuntViewSet):
    """View of Containers.

    Containers are linked to a Well and Well to a Site.

    *NOTE* id_number is the number shared between systems
    and human understandable by the garbade container maintainers.
    unfortunately not unique / humanly maintained so we have our
    own id in the API.

    ?id_number=xxx should work
    """

    permit_list_expands = ['well']

    queryset = (
        Container.objects.all()
        .order_by("id")
        .select_related('well')
        .prefetch_related('well')
        .prefetch_related('container_type')
    )
    serializer_detail_class = ContainerDetailSerializer
    serializer_class = ContainerSerializer
    bbox_filter_field = 'well__geometrie'
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )
    filter_class = ContainerFilter
    ordering_fields = '__all__'


class WellFilter(FilterSet):
    id = filters.CharFilter()
    in_bbox = filters.CharFilter(method='in_bbox_filter', label='bbox')
    no_container = filters.BooleanFilter(
        method='no_container_filter', label='no_container')

    location = filters.CharFilter(
        method="locatie_filter", label='x,y,r')

    stadsdeel = filters.ChoiceFilter(choices=settings.STADSDELEN)
    buurt_code = filters.ChoiceFilter(choices=buurt_choices)

    no_bgt = filters.BooleanFilter(
        method='no_bgt_filter', label='no_bgt_afvalbak')

    in_weg = filters.BooleanFilter(
        method='in_weg_filter', label='in_weg')

    in_pand = filters.BooleanFilter(
        method='in_pand_filter', label='in_pand')

    containers = filters.CharFilter()
    site = filters.CharFilter()

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
            "site",
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

    def in_weg_filter(self, qs, name, value):
        return qs.filter(extra_attributes__in_wegdeel=value)

    def in_pand_filter(self, qs, name, value):
        return qs.filter(extra_attributes__in_pand=value)

    def no_bgt_filter(self, qs, name, value):
        return qs.filter(extra_attributes__missing_bgt_afval=value)


class WellView(DatapuntViewSet):
    """View of Wells."""

    queryset = (
        Well.objects.all()
        .order_by("id")
        .prefetch_related('containers')
    )
    serializer_detail_class = WellSerializer
    serializer_class = WellSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = WellFilter

    ordering_fields = '__all__'


class TypeView(DatapuntViewSet):
    """View of Types."""

    queryset = (
        ContainerType.objects.all()
        .order_by("id")
        .prefetch_related("containers")
    )
    serializer_detail_class = TypeSerializer
    serializer_class = TypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ['volume', 'name']

    ordering_fields = '__all__'


class SiteFilter(FilterSet):
    id = filters.CharFilter()
    in_bbox = filters.CharFilter(method='in_bbox_filter', label='bbox')

    bgt_based = filters.BooleanFilter(
        method='bgt_based_filter', label='BGT basis')

    no_container = filters.BooleanFilter(
        method='no_container_filter', label='No containers')

    no_short_id = filters.BooleanFilter(
        method='no_short_id_filter', label='Missing short_id ')

    location = filters.CharFilter(
        method="locatie_filter", label='x,y,r')

    stadsdeel = filters.ChoiceFilter(choices=settings.STADSDELEN)
    buurt_code = filters.ChoiceFilter(choices=buurt_choices)

    fractie = filters.ChoiceFilter(
        method='fractie_filter',
        choices=settings.WASTE_CHOICES, label="Fractie")

    wells = filters.CharFilter()

    detailed = filters.BooleanFilter(
        method='detailed_filter', label='detailed')

    def detailed_filter(self, qs, name, value):
        """Do nothing trigger detailed serializer."""
        return qs

    class Meta(object):
        model = Site
        fields = (
            "detailed",
            "id",
            "short_id",
            # "buurt_code",
            "stadsdeel",
            # "containers",
            "wells",
            "in_bbox",
            "location",
            "bgt_based",
            "no_container",
            "fractie",
            "no_short_id",
        )

    def locatie_filter(self, qs, name, value):
        point, radius = bbox.parse_xyr(value)
        return qs.filter(centroid__dwithin=(point, radius))

    def in_bbox_filter(self, qs, name, value):
        bbox_values, err = bbox.valid_bbox(value)
        lat1, lon1, lat2, lon2 = bbox_values
        poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        if err:
            raise ValidationError(f"bbox invalid {err}:{bbox_values}")
        return qs.filter(geometrie__bboverlaps=(poly_bbox))

    def bgt_based_filter(self, qs, name, value):
        return qs.filter(bgt_based=value)

    def no_container_filter(self, qs, name, value):
        return qs.filter(wells__containers=None)

    def no_short_id_filter(self, qs, name, value):
        return qs.filter(short_id=None)

    def fractie_filter(self, qs, name, value):
        """Filter on fractie."""
        return qs.filter(wells__containers__waste_name=value).distinct()


class SitePager(HALPagination):
    """Site objects are rather "heavy" so put limits on pagination."""

    page_size = 10
    max_page_size = 9000


class SiteView(DatapuntViewSet):
    """Site's containing wells.

    the ID is a RD coordinate with buurt_code x-y-code

    the short id is streetcode (last 5 digits) + housnumber
    + a row number if street + housenumber is not unique enough.

    Return all information about site.

    - Wells and containers included
    - Fractions
    - Openbare Ruimte Street and Number
    - Centroid

    BGT based sites are unlikely to change.
    the non BGT based sites will most likely still change.

    extra_attributes:
        chauffeur: manual instructions from chauffeur.
    """

    queryset = (
        Site.objects.all()
        .order_by("id")
        .prefetch_related("wells")
        .prefetch_related("fracties")
        .prefetch_related("wells__containers")
        # .prefetch_related("wells__containers__container_type")
    )

    pagination_class = SitePager

    serializer_class = SiteSerializer
    serializer_detail_class = SiteDetailSerializer

    filter_class = SiteFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    lookup_value_regex = '[^/]+'

    ordering_fields = '__all__'


class SiteFractieView(DatapuntViewSet):

    queryset = (
        SiteFractie.objects.all()
        .order_by("id")
        .prefetch_related("site")
    )

    pagination_class = SitePager

    serializer_class = SiteFractieSerializer
    serializer_detail_class = SiteFractieDetailSerializer

    # filter_class = SiteFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    ordering_fields = '__all__'
