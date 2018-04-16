import factory
from random import randint

from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import MultiPolygon

from factory import fuzzy

from parkeervakken_api.models import Parkeervak


vierkantje = Polygon([
        (121849.65, 487303.93),
        (121889.65, 487303.93),
        (121889.65, 487373.93),
        (121849.65, 487303.93)
], srid=28992)


class ParkeervakFactory(factory.DjangoModelFactory):
    class Meta:
        model = Parkeervak

    id = fuzzy.FuzzyText(length=30)
    buurtcode = fuzzy.FuzzyText(length=4)
    stadsdeel = fuzzy.FuzzyText(length=1)
    straatnaam = fuzzy.FuzzyText(length=40)

    # aantal = models.IntegerField(null=True)
    # soort = models.CharField(max_length=20, null=True)
    # type = models.CharField(max_length=20, null=True)
    # e_type = models.CharField(max_length=5, null=True)
    # bord = models.CharField(max_length=50, null=True)
    geometrie = MultiPolygon([vierkantje])
