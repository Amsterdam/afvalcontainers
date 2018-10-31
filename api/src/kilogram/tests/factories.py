import factory
import datetime

from django.contrib.gis.geos import Point
# from django.contrib.gis.geos import Polygon

from factory import fuzzy
from factory.compat import UTC


from kilogram.models import KilogramWeighMeasurement
from kilogram.models import BuurtFractieStatMonth
from kilogram.models import BuurtFractieStatWeek
from kilogram.models import SiteFractieStatWeek
from kilogram.models import SiteFractieStatMonth

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


class SiteFractieStatWeekFactory(factory.DjangoModelFactory):

    class Meta:
        model = SiteFractieStatWeek

    fractie = fuzzy.FuzzyText(length=6)
    week = fuzzy.FuzzyInteger(1, 52)
    year = fuzzy.FuzzyInteger(2000, 2020)
    measurements = fuzzy.FuzzyInteger(0, 3000)
    sum = fuzzy.FuzzyInteger(0, 3000)
    min = fuzzy.FuzzyInteger(0, 3000)
    max = fuzzy.FuzzyInteger(0, 3000)
    avg = fuzzy.FuzzyInteger(0, 3000)
    stddev = fuzzy.FuzzyInteger(0, 3000)


class SiteFractieStatMonthFactory(factory.DjangoModelFactory):

    class Meta:
        model = SiteFractieStatMonth

    fractie = fuzzy.FuzzyText(length=6)
    month = fuzzy.FuzzyInteger(1, 12)
    year = fuzzy.FuzzyInteger(2000, 2020)
    measurements = fuzzy.FuzzyInteger(0, 3000)
    sum = fuzzy.FuzzyInteger(0, 3000)
    min = fuzzy.FuzzyInteger(0, 3000)
    max = fuzzy.FuzzyInteger(0, 3000)
    avg = fuzzy.FuzzyInteger(0, 3000)
    stddev = fuzzy.FuzzyInteger(0, 3000)


class BuurtFractieStatWeekFactory(factory.DjangoModelFactory):

    class Meta:
        model = BuurtFractieStatWeek

    buurt_code = fuzzy.FuzzyText(length=4)
    fractie = fuzzy.FuzzyText(length=6)
    week = fuzzy.FuzzyInteger(1, 52)
    year = fuzzy.FuzzyInteger(2000, 2020)
    measurements = fuzzy.FuzzyInteger(0, 3000)
    sum = fuzzy.FuzzyInteger(0, 3000)
    min = fuzzy.FuzzyInteger(0, 3000)
    max = fuzzy.FuzzyInteger(0, 3000)
    avg = fuzzy.FuzzyInteger(0, 3000)
    stddev = fuzzy.FuzzyInteger(0, 3000)


class BuurtFractieStatMonthFactory(factory.DjangoModelFactory):

    class Meta:
        model = BuurtFractieStatMonth

    buurt_code = fuzzy.FuzzyText(length=4)
    fractie = fuzzy.FuzzyText(length=6)
    month = fuzzy.FuzzyInteger(1, 12)
    year = fuzzy.FuzzyInteger(2000, 2020)
    measurements = fuzzy.FuzzyInteger(0, 3000)
    sum = fuzzy.FuzzyInteger(0, 3000)
    min = fuzzy.FuzzyInteger(0, 3000)
    max = fuzzy.FuzzyInteger(0, 3000)
    avg = fuzzy.FuzzyInteger(0, 3000)
    stddev = fuzzy.FuzzyInteger(0, 3000)


def make_stats_values(site):

    for i in range(5):
        SiteFractieStatWeekFactory(site=site)
        SiteFractieStatMonthFactory(site=site)
        BuurtFractieStatMonthFactory()
        BuurtFractieStatWeekFactory()
