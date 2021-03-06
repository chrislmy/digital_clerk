# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-10 22:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digitalclerk_app', '0013_oauthtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrolment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_code', models.CharField(max_length=50)),
                ('module_name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upi', models.CharField(max_length=15)),
                ('username', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=150)),
                ('department', models.CharField(max_length=150)),
                ('full_name', models.CharField(max_length=150)),
            ],
        ),
        migrations.AddField(
            model_name='enrolment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='digitalclerk_app.UserProfile'),
        ),
    ]
