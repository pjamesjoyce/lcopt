# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sandbox', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sandboxpositions',
            options={'verbose_name': 'Sandbox Position'},
        ),
        migrations.RemoveField(
            model_name='sandboxpositions',
            name='friendlyId',
        ),
    ]
