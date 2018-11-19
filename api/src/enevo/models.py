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
    photo = models.BooleanField()
    last_modified = models.DateTimeField()


class EnevoContainer(models.Model):
    type = models.IntegerField()
    site = models.ForeignKey("EnevoSite",
                             on_delete=models.DO_NOTHING,
                             null=True)
    site_content_type = models.ForeignKey("EnevoSiteContentType",
                                          on_delete=models.DO_NOTHING,
                                          null=True)
    container_slot = models.ForeignKey("EnevoContainerSlot",
                                       on_delete=models.DO_NOTHING,
                                       null=True)
    customer_key = models.CharField(max_length=100, blank=True, null=True)
    last_modified = models.DateTimeField()


class EnevoContainerSlot(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    content_type = models.IntegerField(blank=True, null=True)
    container = models.IntegerField(blank=True, null=True)
    site_content_type = models.ForeignKey("EnevoSiteContentType",
                                          on_delete=models.DO_NOTHING,
                                          null=True)
    site = models.ForeignKey("EnevoSite", on_delete=models.DO_NOTHING,
                             null=True)
    fill_level = models.IntegerField(blank=True, null=True)
    date_when_full = models.DateTimeField(blank=True, null=True)
    last_service_event = models.DateTimeField(blank=True, null=True)
    photo = models.BooleanField(blank=True, null=True)
    last_modified = models.DateTimeField()


class EnevoContainerType(models.Model):
    name = models.CharField(max_length=100)
    volume = models.IntegerField()
    sensor_height = models.FloatField()
    full_height = models.FloatField()
    shape = models.CharField(max_length=100)
    has_bag = models.BooleanField()
    servicing_amount = models.CharField(max_length=100)
    servicing_method = models.CharField(max_length=100)
    last_modified = models.DateTimeField()


class EnevoSiteContentType(models.Model):
    content_type = models.IntegerField()
    content_type_name = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    site = models.ForeignKey("EnevoSite", on_delete=models.DO_NOTHING,
                             null=True)
    fill_level = models.IntegerField(blank=True, null=True)
    date_when_full = models.DateTimeField(blank=True, null=True)
    build_up_rate = models.FloatField(blank=True, null=True)
    fill_up_time = models.IntegerField(blank=True, null=True)
    last_service_event = models.CharField(max_length=100,
                                          blank=True, null=True)
    last_modified = models.CharField(max_length=100)


class EnevoAlert(models.Model):
    type = models.IntegerField()
    type_name = models.CharField(max_length=100)
    reported = models.DateTimeField()
    last_observed = models.DateTimeField()
    site = models.ForeignKey("EnevoSite", on_delete=models.DO_NOTHING)
    site_name = models.CharField(max_length=100, blank=True, null=True)
    area = models.IntegerField()
    area_name = models.CharField(max_length=100)
    content_type = models.IntegerField()
    content_type_name = models.CharField(max_length=100)
    start = models.DateTimeField()


class FillLevel(models.Model):
    time = models.DateTimeField()
    fill_level = models.IntegerField()
    site = models.IntegerField()
    site_name = models.CharField(max_length=100)
    site_content_type = models.IntegerField()
    content_type = models.IntegerField()
    content_type_name = models.CharField(max_length=100)
    confidence = models.IntegerField()
    frozen = models.BooleanField()

    class Meta:
        managed = settings.TESTING
        db_table = 'enevo_filllevel'
