# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-25 13:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kserver_saas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kserver_saas.Template'),
        ),
    ]
