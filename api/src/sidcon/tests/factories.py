import factory
import datetime
import pytz

from django.contrib.gis.geos import Point

from factory import fuzzy

from sidcon.models import SidconFillLevel

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


week1 = datetime.timedelta(days=7)
day1 = datetime.timedelta(days=1)


def get_puntje():

    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class SidconFillLevelFactory(factory.DjangoModelFactory):

    class Meta:
        model = SidconFillLevel

    id = factory.Sequence(lambda n: n)
    _id = factory.Sequence(lambda n: n)
    # do not mess up fill test by going higher then 90
    filling = fuzzy.FuzzyInteger(0, 90)
    valid = True

    scraped_at = fuzzy.FuzzyDateTime(
        datetime.datetime.now().replace(tzinfo=pytz.UTC) - week1,
        datetime.datetime.now().replace(tzinfo=pytz.UTC))

    communication_date_time = fuzzy.FuzzyDateTime(
        datetime.datetime.now().replace(tzinfo=pytz.UTC) - week1,
        datetime.datetime.now().replace(tzinfo=pytz.UTC) - day1)

    geometrie = get_puntje()
