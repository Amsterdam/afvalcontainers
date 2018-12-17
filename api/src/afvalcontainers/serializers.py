# import json
# import logging

from rest_framework import serializers

from datapunt_api.rest import DisplayField
from datapunt_api.rest import LinksField
from datapunt_api.rest import HALSerializer
from datapunt_api.rest import RelatedSummaryField
from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType
from afvalcontainers.models import Site
from afvalcontainers.models import SiteFractie

# from .field_selector import DynamicFieldsMixin
from rest_flex_fields import FlexFieldsModelSerializer


class WellSerializer(HALSerializer):
    _display = DisplayField()

    containers = RelatedSummaryField()

    class Meta(object):
        model = Well
        fields = [
            "_links",
            "_display",
            "id",
            "id_number",
            "serial_number",
            "buurt_code",
            "stadsdeel",
            "geometrie",
            "created_at",
            "warranty_date",
            "operational_date",
            "containers",
            "address",
            "site",
        ]


class ContainerTypeSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = ContainerType
        fields = '__all__'


class ContainerModelSerializer(FlexFieldsModelSerializer):
    """Serializer used by well."""

    class Meta:
        model = Container
        fields = '__all__'

    expandable_fields = {
        'container_type': (
            ContainerTypeSerializer, {
                'source': 'container_type',
                'fields': [
                    'id', 'name',
                    'volume', 'weight',
                ]
            }
        ),
    }


class SiteModelSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Site
        fields = [
            'id',
            'short_id',
            'huisnummer',
            'straatnaam',
            'geometrie',
            'centroid',
            'active',
            'stadsdeel',
            'buurt_code',
        ]


class WellModelSerializer(FlexFieldsModelSerializer):
    """Serializer to use in site detail."""

    containers = ContainerModelSerializer(many=True)

    class Meta:
        model = Well
        fields = '__all__'

    expandable_fields = {
        'site': (
            SiteModelSerializer, {
                'source': 'site',
                'fields': [
                    'id', 'short_id',
                    'geometrie', 'centroid'
                    'straatnaam', 'huisnummer',
                    'buurt', 'active'
                ]
            }),
        'containers': (
            ContainerModelSerializer, {
                'source': 'containers',
                'many': True,
                'fields': [
                    'id', 'id_number',
                    'container_type', 'active',
                ]
            }
        ),
    }


class InlineWellModelSerializer(serializers.ModelSerializer):
    """Serializer to use in site detail."""

    # containers = ContainerModelSerializer(many=True)
    # address = serializers.SerializerMethodField()

    class Meta:
        model = Well
        fields = [
            'id',
            'id_number',
            'serial_number',
            'geometrie',
            'geometrie_rd',
            'buurt_code',
            'site',
        ]


class ContainerSerializer(FlexFieldsModelSerializer, HALSerializer):
    _display = DisplayField()

    container_type = ContainerTypeSerializer()

    address = serializers.SerializerMethodField()
    # well = WellModelSerializer()
    # geometrie = serializers.SerializerMethodField()

    class Meta(object):
        model = Container
        fields = [
            "_links",
            "_display",
            "id",
            "id_number",
            "owner",
            "active",
            "waste_type",
            "waste_name",
            "container_type",
            "warranty_date",
            "operational_date",
            "placing_date",
            "well",
            "address",
        ]

    expandable_fields = {
        'well': (
            WellModelSerializer, {
                'source': 'well',
                'fields': [
                    'id', 'id_number',
                    'geometrie', 'site',
                    'buurt_code'
                ]
            }
        ),
    }

    def get_address(self, obj):
        if obj.well:
            return obj.well.address.get('summary')


class ContainerDetailSerializer(ContainerSerializer):

    well = InlineWellModelSerializer()

    # def get_geometrie(self, obj):
    #     if obj.well:
    #         return obj.well.geometrie


class TypeSerializer(HALSerializer):
    _display = DisplayField()

    containers = RelatedSummaryField()

    class Meta(object):
        model = ContainerType
        fields = [
            "_links",
            "_display",
            "id",
            "name",
            "volume",
            "weight",
            "containers"
        ]


def fracties(obj):
    fracties = {}
    containers = {}
    volumes = {}

    for f in obj.fracties.all():
        containers[f.fractie] = f.containers
        volumes[f.fractie] = f.volume_m3

    fracties['containers'] = containers
    fracties['volumes_m3'] = volumes

    return fracties


class SiteFractieSerializer(FlexFieldsModelSerializer, HALSerializer):

    _display = DisplayField()

    class Meta:
        model = SiteFractie
        fields = [
            "_links",
            '_display',
            'site',
            'fractie',
            'volume_m3',
            'containers',
        ]

    expandable_fields = {
        'site': (
            SiteModelSerializer, {
                'fields': [
                    'id',
                    'short_id',
                    'buurt_code',
                    'straatnaam',
                    'huisnummer',
                ]
            }
        ),
    }


class SiteFractieDetailSerializer(FlexFieldsModelSerializer, HALSerializer):

    _display = DisplayField()

    class Meta:
        model = SiteFractie
        fields = [
            # "_links",
            "_display",
            # 'site_id',
            "site",
            # 'site',
            'fractie',
            'volume_m3',
            'containers',
        ]

    expandable_fields = {
        'site': (
            SiteModelSerializer, {
                'fields': [
                    'id',
                    'short_id',
                    'centroid'
                    'buurt_code',
                ]
            }
        ),
    }


class SiteSerializer(FlexFieldsModelSerializer, HALSerializer):

    _display = DisplayField()
    wells = RelatedSummaryField()
    fracties = serializers.SerializerMethodField()

    class Meta(object):
        model = Site

        fields = [
            "_links",
            "_display",
            "id",
            "short_id",
            "stadsdeel",
            "straatnaam",
            "huisnummer",
            "wells",
            "fracties",
            "centroid",
        ]

    def get_fracties(self, obj):
        return fracties(obj)

    expandable_fields = {
        'wells': (
            WellModelSerializer, {
                'source': 'wells',
                'many': True,
                'fields': [
                    'id', 'id_number',
                    'geometrie', 'site',
                    'buurt_code'
                ]
            }
        ),
    }


class SiteDetailSerializer(HALSerializer):

    _display = DisplayField()
    wells = WellModelSerializer(many=True)
    fracties = serializers.SerializerMethodField()
    distance_to_address = serializers.IntegerField(source='distance')

    class Meta(object):
        model = Site

        fields = [
            "_links",
            "_display",
            "id",
            "short_id",
            "stadsdeel",
            "buurt_code",
            "straatnaam",
            "huisnummer",
            "wells",
            "fracties",
            "bgt_based",
            "extra_attributes",
            "centroid",
            "geometrie",
            "distance_to_address",
        ]

    def get_fracties(self, obj):
        return fracties(obj)
