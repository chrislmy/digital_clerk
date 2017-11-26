# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-25 22:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digitalclerk_app', '0010_auto_20171120_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedBack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecturer', models.IntegerField()),
                ('next_steps', models.CharField(max_length=300)),
                ('foot_note', models.CharField(max_length=300)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='digitalclerk_app.Request')),
            ],
        ),
    ]