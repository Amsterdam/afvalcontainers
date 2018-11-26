from rest_framework import serializers

from datapunt_api.rest import DisplayField
from datapunt_api.rest import HALSerializer
from datapunt_api.rest import RelatedSummaryField
from enevo.models import EnevoContainer
from enevo.models import EnevoSite
from enevo.models import EnevoContainerType
from enevo.models import EnevoContainerSlot
from enevo.models import EnevoSiteContentType
from enevo.models import EnevoAlert
from enevo.models import EnevoContentType


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnevoContentType
        fields = '__all__'


class ContainerTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnevoContainerType
        fields = '__all__'


class ContainerSlotSerializer(serializers.ModelSerializer):
    containers = RelatedSummaryField()

    class Meta:
        model = EnevoContainerSlot
        fields = '__all__'


class SiteDetailSerializer(serializers.ModelSerializer):
    containers = RelatedSummaryField()
    container_slots = RelatedSummaryField()
    site_content_types = RelatedSummaryField()
    alerts = RelatedSummaryField()

    class Meta:
        model = EnevoSite
        fields = '__all__'


class SiteSerializer(serializers.ModelSerializer):
    containers = RelatedSummaryField()

    class Meta:
        model = EnevoSite
        fields = '__all__'


class SiteContentTypeSerializer(serializers.ModelSerializer):
    container_slots = RelatedSummaryField()
    containers = RelatedSummaryField()

    class Meta:
        model = EnevoSiteContentType
        fields = '__all__'


class AlertSerializer(HALSerializer):

    class Meta:
        model = EnevoAlert
        fields = '__all__'


class InlineContainerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnevoContainerType
        fields = [
            "id",
            "name",
            "volume",
            "full_height",
            "shape"
        ]


class ContainerDetailSerializer(serializers.ModelSerializer):
    _display = DisplayField()

    class Meta:
        model = EnevoContainer
        fields = '__all__'
        depth = 1


class ContainerSerializer(HALSerializer):
    _display = DisplayField()
    container_type = InlineContainerTypeSerializer()

    class Meta:
        model = EnevoContainer
        fields = (
            '_links',
            '_display',
            'id',
            'container_type',
            'site',
            'site_content_type',
            'container_slot',
            'geometrie',
            'geometrie_rd',
            'geo_accuracy',
            'customer_key',
            'last_modified',
            'valid'
        )
