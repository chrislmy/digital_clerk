# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-27 02:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalclerk_app', '0016_helpstaff'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpstaff',
            name='module_code',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='helpstaff',
            name='module_name',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
    ]