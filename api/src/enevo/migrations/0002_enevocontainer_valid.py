# Generated by Django 2.1.2 on 2018-11-23 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enevo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enevocontainer',
            name='valid',
            field=models.NullBooleanField(),
        ),
    ]