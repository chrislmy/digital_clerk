# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-18 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalclerk_app', '0006_interaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interaction',
            name='time_closed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
