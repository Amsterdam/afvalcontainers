# Generated by Django 2.1.4 on 2018-12-24 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afvalcontainers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='buurt_code',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='stadsdeel',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='stadsdeel_naam',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='straatnaam',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
