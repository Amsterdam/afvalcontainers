import factory
from random import randint

from django.contrib.gis.geos import Point

from factory import fuzzy


from afvalcontainers.models import Container
from afvalcontainers.models import Well
from afvalcontainers.models import ContainerType

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


def get_puntje():

    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class ContainerFactory(factory.DjangoModelFactory):

    class Meta:
        model = Container

    id = factory.Sequence(lambda n: n)
    owner = {}
    serial_number = fuzzy.FuzzyText(length=4)
    id_number = fuzzy.FuzzyText(length=10)
    active = fuzzy.FuzzyChoice([True, False])
    waste_type = fuzzy.FuzzyInteger(0, 42)


class WellFactory(factory.DjangoModelFactory):

    class Meta:
        model = Well

    id = factory.Sequence(lambda n: n)
    owner = {}
    buurt_code = fuzzy.FuzzyText(length=4)
    stadsdeel = fuzzy.FuzzyText(length=1)
    address = fuzzy.FuzzyText(length=40)
    geometrie = get_puntje()


class ContainerTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = ContainerType

    id = factory.Sequence(lambda n: n)
    name = fuzzy.FuzzyText(length=40)
    volume = fuzzy.FuzzyInteger(0, 42)
