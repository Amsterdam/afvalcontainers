import factory
import datetime

from django.contrib.gis.geos import Point
# from django.contrib.gis.geos import Polygon

from factory import fuzzy
from factory.compat import UTC


from kilogram.models import KilogramWeighMeasurement

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


def get_puntje():
    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class KiloFactory(factory.DjangoModelFactory):

    class Meta:
        model = KilogramWeighMeasurement

    id = factory.Sequence(lambda n: n)
    buurt_code = fuzzy.FuzzyText(length=4)
    stadsdeel = fuzzy.FuzzyText(length=1)
    seq_id = fuzzy.FuzzyInteger(1, 2000)
    weigh_at = fuzzy.FuzzyDateTime(
        datetime.datetime(2018, 10, 16, tzinfo=UTC)
    )
    first_weight = fuzzy.FuzzyInteger(1, 2000)
    second_weight = fuzzy.FuzzyInteger(1000, 3000)
    net_weight = fuzzy.FuzzyInteger(1000, 3000)
    geometrie = get_puntje()
