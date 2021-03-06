from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings

"""
{
     "id": 9136,
     "well": 9135,
     "owner": {"id": 111, "name": "M Oost"},
     "active": true,
     "id_number": "RE 9692",
     "created_at": "2012-03-29T12:00:00+02:00",
     "waste_type": 1,
     "placing_date": null,
     "serial_number": "BAO00970",
     "warranty_date": "2014-03-20T00:00:00+01:00",
     "container_type": 350,
     "empty_frequency": null,
     "operational_date": null
}
"""


class Container(models.Model):
    """Container object."""

    id = models.IntegerField(primary_key=True)
    id_number = models.CharField(max_length=35, null=False, db_index=True)
    serial_number = models.CharField(max_length=45, null=False, db_index=True)
    owner = JSONField(null=True)
    well = models.ForeignKey(
        'Well', null=True,
        related_name="containers", on_delete=models.DO_NOTHING
    )
    active = models.IntegerField(null=True)
    waste_type = models.IntegerField(null=True, db_index=True)
    waste_name = models.CharField(max_length=20, db_index=True)

    container_type = models.ForeignKey(
        "ContainerType", related_name="containers", on_delete=models.DO_NOTHING
    )

    created_at = models.DateTimeField(null=True)
    placing_date = models.DateTimeField(null=True)
    operational_date = models.DateTimeField(null=True)
    warranty_date = models.DateTimeField(null=True)


"""
{
    "id": 2829,
    "owner": {"id": 16, "name": "F Nieuw-West"},
    "active": true,
    "location": {
        "address": {
            "summary": "Jan Evertsenstraat 717, Amsterdam",
            "district": "F86 - Overtoomse Veld",
            "neighbourhood": "86a - Overtoomse Veld Noord"
        },
        "position": {
            "latlng": {
                "lat": "52.3698168", "lng": "4.8357449"
            },
            "latitude": "52.3698168",
            "longitude": "4.8357449"
        }
    },
    "id_number": "WLREF31242",
    "containers": [2830],
    "created_at": "2010-09-22T11:55:35+02:00",
    "placing_date": null,
    "serial_number": "WL118921",
    "warranty_date": "2028-12-31T00:00:00+01:00",
    "operational_date": null
}
"""


class Well(models.Model):
    """Wells contain containers."""

    id = models.IntegerField(primary_key=True)
    id_number = models.CharField(max_length=35, db_index=True)
    serial_number = models.CharField(max_length=45, db_index=True)
    active = models.IntegerField(null=True)

    owner = JSONField()

    containers_bron = JSONField()

    geometrie = models.PointField(name="geometrie", srid=4326)
    geometrie_rd = models.PointField(
        name="geometrie_rd", srid=28992, null=True)

    stadsdeel = models.CharField(null=True, max_length=1)
    buurt_code = models.CharField(null=True, max_length=4)
    address = JSONField(null=True)

    created_at = models.DateTimeField(null=True)
    placing_date = models.DateTimeField(null=True)
    warranty_date = models.DateTimeField(null=True)
    operational_date = models.DateTimeField(null=True)

    extra_attributes = JSONField(default=dict)

    site = models.ForeignKey(
        'Site', null=True,
        related_name="wells", on_delete=models.SET_NULL
    )


class Site(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    short_id = models.IntegerField(unique=True, null=True)
    buurt_code = models.CharField(max_length=20, null=True)
    stadsdeel = models.CharField(max_length=1, null=True)
    stadsdeel_naam = models.CharField(max_length=20, null=True)
    straatnaam = models.CharField(max_length=40, null=True)
    huisnummer = models.IntegerField(null=True)
    # distance to address
    distance = models.IntegerField(null=True)
    bgt_based = models.NullBooleanField()
    centroid = models.PointField(name='centroid', srid=4326)
    geometrie = models.PolygonField(name='geometrie', srid=28992)
    extra_attributes = JSONField(null=True, default=dict)
    # helper field during cleanup. do not publish.
    active = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.id}-{self.straatnaam} {self.huisnummer}"


class SiteFractie(models.Model):
    """Fractie capaciteit."""

    site = models.ForeignKey(
        'Site', null=True,
        related_name="fracties", on_delete=models.SET_NULL
    )

    # AKA waste name
    fractie = models.CharField(max_length=20, db_index=True)
    containers = models.IntegerField(null=True, default=0)
    volume_m3 = models.DecimalField(
        null=True, default=0, max_digits=6, decimal_places=3)

    def __str__(self):
        return f'{self.fractie} - {self.volume_m3} - {self.site.short_id}'


class ContainerType(models.Model):
    """Contains volumne information aboud containers."""

    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    volume = models.DecimalField(
        null=True, default=0, max_digits=6, decimal_places=3)

    weight = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} - {self.volume}M3"


class Buurten(models.Model):
    ogc_fid = models.IntegerField(primary_key=True)
    id = models.CharField(max_length=14)
    vollcode = models.CharField(max_length=4)
    naam = models.CharField(max_length=40)

    class Meta:
        db_table = 'buurt_simple'
        managed = settings.TESTING
