import factory
import datetime
import pytz

from django.contrib.gis.geos import Point

from factory import fuzzy

from sidcon.models import SidconFillLevel

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


week1 = datetime.timedelta(days=7)


def get_puntje():

    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class SidconFillLevelFactory(factory.DjangoModelFactory):

    class Meta:
        model = SidconFillLevel

    id = factory.Sequence(lambda n: n)
    _id = factory.Sequence(lambda n: n)
    filling = fuzzy.FuzzyInteger(0, 100)
    valid = True

    scraped_at = fuzzy.FuzzyDateTime(
        datetime.datetime.now().replace(tzinfo=pytz.UTC) - week1,
        datetime.datetime.now().replace(tzinfo=pytz.UTC))

    geometrie = get_puntje()
