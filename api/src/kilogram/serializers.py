from datapunt_api.rest import HALSerializer
# from datapunt_api.rest import DisplayField
from rest_framework import serializers

from kilogram.models import KilogramWeighMeasurement
from kilogram.models import SiteFractieStatWeek
from kilogram.models import SiteFractieStatMonth
from kilogram.models import BuurtFractieStatMonth
from kilogram.models import BuurtFractieStatWeek


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
            'buurt_code',
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
            'location',
            'fractie',
            'container_ids',
            'stadsdeel',
            'buurt_code',
            'site_id',
            'first_weight',
            'second_weight',
            'net_weight',
            'geometrie',
            'valid',
        ]


class SiteFractieStatWeekSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteFractieStatWeek
        fields = '__all__'


class SiteFractieStatMonthSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteFractieStatMonth
        fields = '__all__'


class BuurtFractieStatWeekSerializer(serializers.ModelSerializer):

    class Meta:
        model = BuurtFractieStatWeek
        fields = '__all__'


class BuurtFractieStatMonthSerializer(serializers.ModelSerializer):

    class Meta:
        model = BuurtFractieStatMonth
        fields = '__all__'
