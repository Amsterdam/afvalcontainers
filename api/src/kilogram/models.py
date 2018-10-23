from django.contrib.gis.db import models
from django.conf import settings


class KilogramWeighMeasurement(models.Model):
    id = models.IntegerField(primary_key=True)
    seq_id = models.IntegerField(blank=True, null=True)
    system_id = models.IntegerField(blank=True, null=True)
    weigh_at = models.DateTimeField(blank=True, null=True)
    location_id = models.IntegerField(blank=True, null=True)
    container_id = models.CharField(max_length=200, blank=True, null=True)
    fractie = models.CharField(max_length=200, blank=True, null=True)
    stadsdeel = models.CharField(max_length=1, blank=True, null=True)
    buurt_code = models.CharField(max_length=4, blank=True, null=True)
    first_weight = models.IntegerField(blank=True, null=True)
    second_weight = models.IntegerField(blank=True, null=True)
    net_weight = models.IntegerField(blank=True, null=True)
    site_id = models.IntegerField(blank=True, null=True)
    geometrie = models.PointField(blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = 'kilogram_weigh_measurement'
