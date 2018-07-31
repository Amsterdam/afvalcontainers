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
    # container_type = ContainerTypeSerializer()
    # address = serializers.SerializerMethodField()

    class Meta:
        model = Well
        fields = '__all__'


class ContainerSerializer(HALSerializer):
    _display = DisplayField()

    container_type = ContainerTypeSerializer()

    address = serializers.SerializerMethodField()
    # well = WellSerializer()

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
    for w in obj.wells.all():
        for c in w.containers.all():
            count = fracties.setdefault(c.waste_name, 0) + 1
            fracties[c.waste_name] = count

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
