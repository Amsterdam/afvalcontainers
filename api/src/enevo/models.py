from django.contrib.gis.db import models

from django.conf import settings


class EnevoSite(models.Model):
    type = models.IntegerField()
    name = models.CharField(max_length=100, null=True, blank=True)
    area = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    # dutch name kept to avoid confusion
    geometrie = models.PointField(name="geometrie", srid=4326)
    geometrie_rd = models.PointField(
        name="geometrie_rd", srid=28992, null=True)
    photo = models.NullBooleanField()
    last_modified = models.DateTimeField()


class EnevoContainer(models.Model):
    container_type_id = models.IntegerField(null=True)
    site_id = models.IntegerField(null=True)
    site_content_type_id = models.IntegerField(null=True)
    container_slot_id = models.IntegerField(null=True)

    geometrie = models.PointField(name="geometrie", srid=4326, null=True)
    geometrie_rd = models.PointField(
        name="geometrie_rd", srid=28992, null=True)
    geo_accuracy = models.IntegerField(null=True)
    customer_key = models.CharField(max_length=100, blank=True, null=True)
    last_modified = models.DateTimeField()
    valid = models.NullBooleanField()


class EnevoContainerSlot(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    content_type_id = models.IntegerField(null=True)
    container = models.IntegerField(blank=True, null=True)
    site_content_type_id = models.IntegerField(null=True)
    site_id = models.IntegerField(null=True)
    site_fk = models.IntegerField(null=True)
    site_content_type_fk = models.IntegerField(null=True)
    fill_level = models.IntegerField(blank=True, null=True)
    date_when_full = models.DateTimeField(blank=True, null=True)
    last_service_event = models.DateTimeField(blank=True, null=True)
    photo = models.NullBooleanField(blank=True, null=True)
    last_modified = models.DateTimeField()


class EnevoContainerType(models.Model):
    name = models.CharField(max_length=100)
    volume = models.IntegerField()
    sensor_height = models.FloatField()
    full_height = models.FloatField()
    shape = models.CharField(max_length=100)
    has_bag = models.NullBooleanField()
    servicing_amount = models.CharField(max_length=100)
    servicing_method = models.CharField(max_length=100)
    last_modified = models.DateTimeField()


class EnevoSiteContentType(models.Model):
    content_type_id = models.IntegerField(null=True)
    content_type_name = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    site_id = models.IntegerField(null=True)
    fill_level = models.IntegerField(blank=True, null=True)
    date_when_full = models.DateTimeField(blank=True, null=True)
    build_up_rate = models.FloatField(blank=True, null=True)
    fill_up_time = models.IntegerField(blank=True, null=True)
    last_service_event = models.CharField(
        max_length=100, blank=True, null=True)
    last_modified = models.CharField(max_length=100)


class EnevoContentType(models.Model):
    category = models.IntegerField()
    category_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    weight_to_volume_ratio = models.FloatField()
    last_modified = models.CharField(max_length=100)


class EnevoAlert(models.Model):
    type = models.IntegerField()
    type_name = models.CharField(max_length=100)
    reported = models.DateTimeField()
    last_observed = models.DateTimeField()
    site = models.ForeignKey(
        "EnevoSite",
        related_name="alerts",
        on_delete=models.DO_NOTHING)
    site_name = models.CharField(max_length=100, blank=True, null=True)
    area = models.IntegerField()
    area_name = models.CharField(max_length=100)
    content_type = models.ForeignKey(
        "EnevoContentType",
        related_name="alerts",
        on_delete=models.DO_NOTHING,
        null=True)
    content_type_name = models.CharField(max_length=100)
    start = models.DateTimeField()

    class Meta:
        managed = settings.TESTING
        db_table = 'enevo_alert'


class EnevoFillLevel(models.Model):
    time = models.DateTimeField()
    fill_level = models.IntegerField()
    e_site = models.IntegerField()
    e_site_name = models.CharField(max_length=100)
    e_site_content_type = models.IntegerField()
    content_type = models.IntegerField()
    content_type_name = models.CharField(max_length=100)
    confidence = models.IntegerField()
    frozen = models.NullBooleanField()

    class Meta:
        managed = settings.TESTING
        db_table = 'enevo_filllevel'
