from django.contrib.gis.db import models
from django.conf import settings
from afvalcontainers.models import Site


class KilogramWeighMeasurement(models.Model):
    id = models.IntegerField(primary_key=True)
    seq_id = models.IntegerField(blank=True, null=True)
    system_id = models.IntegerField(blank=True, null=True)
    weigh_at = models.DateTimeField(blank=True, null=True)
    location = models.IntegerField(blank=True, null=True)
    container_ids = models.CharField(max_length=200, blank=True, null=True)
    container_count = models.IntegerField(blank=True, null=True),
    fill_chance = models.FloatField(blank=True, null=True),
    fill_level = models.FloatField(blank=True, null=True),
    fractie = models.CharField(max_length=200, blank=True, null=True)
    stadsdeel = models.CharField(max_length=1, blank=True, null=True)
    buurt_code = models.CharField(max_length=4, blank=True, null=True)
    first_weight = models.IntegerField(blank=True, null=True)
    second_weight = models.IntegerField(blank=True, null=True)
    net_weight = models.IntegerField(blank=True, null=True)
    site_id = models.IntegerField(blank=True, null=True)
    geometrie = models.PointField(blank=True, null=True)
    valid = models.NullBooleanField()

    class Meta:
        managed = settings.TESTING
        db_table = 'kilogram_weigh_measurement'


class SiteFractieStatWeek(models.Model):
    site = models.ForeignKey(
        Site, to_field='short_id', on_delete=models.CASCADE,
        related_name='weekstats'
    )
    fractie = models.CharField(max_length=20, null=False)
    week = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    wegingen = models.IntegerField(null=True, blank=True)
    sum = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    avg = models.IntegerField(null=True, blank=True)
    stddev = models.IntegerField(null=True, blank=True)


class SiteFractieStatMonth(models.Model):
    site = models.ForeignKey(
        Site, to_field='short_id', on_delete=models.CASCADE,
        related_name='monthstats'
    )
    fractie = models.CharField(max_length=20, null=False)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    wegingen = models.IntegerField(null=True, blank=True)
    sum = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    avg = models.IntegerField(null=True, blank=True)
    stddev = models.IntegerField(null=True, blank=True)


class BuurtFractieStatMonth(models.Model):
    buurt_code = models.CharField(max_length=4, null=False, db_index=True)
    fractie = models.CharField(max_length=20, null=False, db_index=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    month = models.IntegerField(null=True, blank=True, db_index=True)
    wegingen = models.IntegerField(null=True, blank=True, db_index=True)
    sum = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    avg = models.IntegerField(null=True, blank=True)
    stddev = models.IntegerField(null=True, blank=True)
    inhabitants = models.IntegerField(null=True, blank=True)


class BuurtFractieStatWeek(models.Model):
    buurt_code = models.CharField(max_length=4, null=False, db_index=True)
    fractie = models.CharField(max_length=20, null=False, db_index=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    week = models.IntegerField(null=True, blank=True, db_index=True)
    wegingen = models.IntegerField(null=True, blank=True, db_index=True)
    sum = models.IntegerField(null=True, blank=True)
    min = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    avg = models.IntegerField(null=True, blank=True)
    stddev = models.IntegerField(null=True, blank=True)
    inhabitants = models.IntegerField(null=True, blank=True)
