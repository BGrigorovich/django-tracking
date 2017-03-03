# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_auto_20160525_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='email',
            field=models.CharField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
