from django.contrib.gis.db import models
from django.conf import settings
# from afvalcontainers.models import Site


class SidconFillLevel(models.Model):
    """Container with sensors."""

    class Meta:
        managed = settings.TESTING
        db_table = 'sidcon_container_states'

    id = models.IntegerField(primary_key=True)
    scraped_at = models.DateTimeField(blank=True, null=True)
    placement_date = models.DateTimeField(blank=True, null=True)
    communication_date_time = models.DateTimeField(blank=True, null=True)
    geometrie = models.PointField(blank=True, null=True)
    valid = models.NullBooleanField()
    _id = models.IntegerField()

    filling = models.IntegerField(blank=True, null=True)
    device_id = models.IntegerField(blank=True, null=True)
    entity_id = models.IntegerField(blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    limit_full = models.IntegerField(blank=True, null=True)
    limit_near_full = models.IntegerField(blank=True, null=True)
    nr_press_strokes = models.IntegerField(blank=True, null=True)
    drum_action_count = models.IntegerField(blank=True, null=True)
    network_strenght = models.IntegerField(blank=True, null=True)
    status_incidents = models.IntegerField(blank=True, null=True)
    max_nr_press_strokes = models.IntegerField(blank=True, null=True)
    drum_position_status = models.IntegerField(blank=True, null=True)
    lock_position_status = models.IntegerField(blank=True, null=True)
    nr_press_strokes_to_go = models.IntegerField(blank=True, null=True)
    total_nr_press_strokes = models.IntegerField(blank=True, null=True)
    total_nr_empty_detected = models.IntegerField(blank=True, null=True)
    max_dump_count_on_dump_location = models.IntegerField(blank=True, null=True)    # noqa
    successfull_transaction_since_reset = models.IntegerField(blank=True, null=True) # noqa
    unsuccessfull_transaction_since_reset = models.IntegerField(blank=True, null=True) # noqa

    container_id = models.IntegerField(blank=True, null=True),
    house_number = models.IntegerField(blank=True, null=True),
    press_status = models.IntegerField(blank=True, null=True),
    press_current = models.IntegerField(blank=True, null=True),

    description = models.CharField(max_length=200, blank=True, null=True)
    status_device = models.CharField(max_length=50, blank=True, null=True)
    container_name = models.CharField(max_length=50, blank=True, null=True)
    status_chip_cards = models.CharField(max_length=50, blank=True, null=True)
    status_container = models.CharField(max_length=50, blank=True, null=True)
    status_trigger_name = models.CharField(max_length=100, blank=True, null=True)  # noqa
    status_configuration = models.CharField(max_length=50, blank=True, null=True)  # noqa

    battery_voltage = models.FloatField(blank=True, null=True),
    volume_correction_factor = models.FloatField(blank=True, null=True),

    fraction = models.CharField(max_length=50, blank=True, null=True)

    # stadsdeel = models.CharField(max_length=1, blank=True, null=True)
    # buurt_code = models.CharField(max_length=4, blank=True, null=True)
    # first_weight = models.IntegerField(blank=True, null=True)
    # second_weight = models.IntegerField(blank=True, null=True)
    # net_weight = models.IntegerField(blank=True, null=True)
    # site_id = models.IntegerField(blank=True, null=True)
