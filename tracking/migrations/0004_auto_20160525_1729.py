# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_auto_20141023_0834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannedip',
            name='ip_address',
            field=models.GenericIPAddressField(help_text='The IP address that should be banned', verbose_name=b'IP Address'),
        ),
    ]
