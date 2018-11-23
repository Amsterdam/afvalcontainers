import factory

from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from django.utils import timezone

from factory import fuzzy

from enevo.models import EnevoContainer
from enevo.models import EnevoSite
from enevo.models import EnevoContainerType
from enevo.models import EnevoContainerSlot
from enevo.models import EnevoSiteContentType
from enevo.models import EnevoAlert
from enevo.models import EnevoContentType

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


def get_puntje():

    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class ContainerSlotFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoContainerSlot

    id = factory.Sequence(lambda n: n)
    fill_level = fuzzy.FuzzyInteger(0, 100)
    date_when_full = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    last_service_event = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class ContainerTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoContainerType

    id = factory.Sequence(lambda n: n)
    name = fuzzy.FuzzyText(length=40)
    volume = fuzzy.FuzzyInteger(0, 50)
    sensor_height = fuzzy.FuzzyFloat(0.5, 100.0)
    full_height = fuzzy.FuzzyFloat(0.5, 100.0)
    shape = fuzzy.FuzzyText(length=20)
    has_bag = fuzzy.FuzzyInteger(0, 1)
    servicing_amount = fuzzy.FuzzyText(length=20)
    servicing_method = fuzzy.FuzzyText(length=20)
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class SiteFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoSite

    id = factory.Sequence(lambda n: n)
    type = fuzzy.FuzzyInteger(0, 1)
    geometrie = get_puntje()
    photo = fuzzy.FuzzyInteger(0, 1)
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class SiteContentTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoSiteContentType

    id = factory.Sequence(lambda n: n)
    content_type_name = fuzzy.FuzzyText(length=30)
    category_name = fuzzy.FuzzyText(length=30)
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class ContentTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoContentType

    id = factory.Sequence(lambda n: n)
    category = fuzzy.FuzzyInteger(0, 50)
    category_name = fuzzy.FuzzyText(length=30)
    name = fuzzy.FuzzyText(length=30)
    state = fuzzy.FuzzyText(length=30)
    weight_to_volume_ratio = fuzzy.FuzzyFloat(0.5, 100.0)
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class ContainerFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoContainer

    id = factory.Sequence(lambda n: n)
    customer_key = fuzzy.FuzzyText(length=10)
    geometrie = get_puntje()
    geo_accuracy = fuzzy.FuzzyInteger(0, 50)
    last_modified = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class AlertFactory(factory.DjangoModelFactory):

    class Meta:
        model = EnevoAlert

    id = factory.Sequence(lambda n: n)
    type = fuzzy.FuzzyInteger(0, 50)
    type_name = fuzzy.FuzzyText(length=30)
    reported = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    last_observed = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    site_name = fuzzy.FuzzyText(length=30)
    area = fuzzy.FuzzyInteger(0, 50)
    area_name = fuzzy.FuzzyText(length=30)
    content_type_name = fuzzy.FuzzyText(length=30)
    start = fuzzy.FuzzyDateTime(start_dt=timezone.now())
