# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-15 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='articles',
            field=models.ManyToManyField(null=True, to='app.Article'),
        ),
    ]
