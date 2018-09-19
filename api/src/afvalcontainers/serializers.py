# import json
# import logging

from rest_framework import serializers

from datapunt_api.rest import DisplayField
from datapunt_api.rest import HALSerializer
from datapunt_api.rest import RelatedSummaryField
from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType
from afvalcontainers.models import Site


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


class ContainerModelSerializer(serializers.ModelSerializer):
    """Serializer used by well
    """

    class Meta:
        model = Container
        fields = '__all__'


class ContainerTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContainerType
        fields = '__all__'


class WellModelSerializer(serializers.ModelSerializer):
    """ Serializer to use in site detail
    """
    containers = ContainerModelSerializer(many=True)
    # address = serializers.SerializerMethodField()


    class Meta:
        model = Well
        fields = '__all__'


class InlineWellModelSerializer(serializers.ModelSerializer):
    """ Serializer to use in site detail
    """
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


class ContainerSerializer(HALSerializer):
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
            "containers"
        ]


def fracties(obj):
    fracties = {}
    containers = {}
    volumes = {}

    for w in obj.wells.all():
        for c in w.containers.all():
            count = containers.setdefault(c.waste_name, 0) + 1
            volume = volumes.setdefault(c.waste_name, 0)
            volume += c.container_type.volume
            containers[c.waste_name] = count
            volumes[c.waste_name] = volume

    fracties['containers'] = containers
    fracties['volumes_m3'] = volumes

    return fracties


class SiteSerializer(HALSerializer):

    _display = DisplayField()
    wells = RelatedSummaryField()
    # wells__containers = RelatedSummaryField()
    fracties = serializers.SerializerMethodField()

    class Meta(object):
        model = Site

        fields = [
            "_links",
            "_display",
            "id",
            "stadsdeel",
            "straatnaam",
            "huisnummer",
            "wells",
            "fracties",
            "centroid",
        ]

    def get_fracties(self, obj):
        return fracties(obj)


class SiteDetailSerializer(HALSerializer):

    _display = DisplayField()
    wells = WellModelSerializer(many=True)
    fracties = serializers.SerializerMethodField()

    class Meta(object):
        model = Site

        fields = [
            "_links",
            "_display",
            "id",
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
        ]

    def get_fracties(self, obj):
        return fracties(obj)
