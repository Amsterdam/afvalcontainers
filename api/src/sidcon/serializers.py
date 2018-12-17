
from rest_framework import serializers
from sidcon.models import SidconFillLevel
from datapunt_api.rest import HALSerializer
from rest_flex_fields import FlexFieldsModelSerializer


class SidconSerializer(FlexFieldsModelSerializer):

    container_id = serializers.CharField(source='description')

    class Meta:
        model = SidconFillLevel

        fields = [
            'filling',
            'communication_date_time',
            'id',
            'container_id',
        ]


class SidconDetailSerializer(FlexFieldsModelSerializer, HALSerializer):

    container_id = serializers.CharField(source='description')

    class Meta:
        model = SidconFillLevel

        fields = '__all__'
