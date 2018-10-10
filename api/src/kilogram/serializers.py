from datapunt_api.rest import HALSerializer
# from datapunt_api.rest import DisplayField
from kilogram.models import KilogramWeighMeasurement


class KilogramSerializer(HALSerializer):

    class Meta(object):
        model = KilogramWeighMeasurement
        fields = [
            'id',
            'seq_id',
            'system_id',
            'weigh_at',
            'fractie',
            'site_id',
            'first_weight',
            'second_weight',
            'net_weight',
        ]


class KilogramDetailSerializer(HALSerializer):

    class Meta(object):
        model = KilogramWeighMeasurement
        fields = [
            'id',
            'seq_id',
            'system_id',
            'weigh_at',
            'location_id',
            'fractie',
            'container_id',
            'site_id',
            'first_weight',
            'second_weight',
            'net_weight',
            'geometrie',
        ]
