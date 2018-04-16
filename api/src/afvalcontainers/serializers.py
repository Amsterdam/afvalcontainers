# import json
# import logging

# from rest_framework import serializers

from datapunt_api.rest import DisplayField
from datapunt_api.rest import HALSerializer
from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType


class ContainerSerializer(HALSerializer):
    _display = DisplayField()

    class Meta(object):
        model = Container
        fields = [
            "_links",
            "_display",
            "id",
            "buurtcode",
            "straatnaam",
            "aantal",
            "type",
            "geometrie"

            "warranty_date",
            "operational_date",
            "placing_date",
        ]


class WellSerializer(HALSerializer):
    _display = DisplayField()

    class Meta(object):
        model = Well
        fields = [
            "_links",
            "_display",
            "id",
            "id_number",
            "serial_number",
            "buurt_code",
            "geometrie",
            "created_at",
            "warranty_date",
            "operational_date",
        ]


class TypeSerializer(HALSerializer):
    _display = DisplayField()

    class Meta(object):
        model = ContainerType
        fields = [
            "_links",
            "_display",
            "id",
            "name",
            "volume",
        ]
