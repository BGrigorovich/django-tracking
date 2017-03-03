"""Populate `Visitor.email` with data from related user"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# TODO: commit to rep


def forwards(apps, schema_editor):
    visitor_model = apps.get_model('tracking', 'visitor')
    user_model = apps.get_model('auth', 'user')

    users = user_model.objects.filter(visitor__isnull=False)
    emails = {x[0]: x[1] for x in users.values_list('id', 'email').distinct()}
    qs = visitor_model.objects.all()
    visitors = qs.filter(user__isnull=False)
    for visitor in visitors:
        email = emails[visitor.user_id]
        qs.filter(id=visitor.id).update(email=email)


def backwards(apps, schema_editor):
    visitor_model = apps.get_model('tracking', 'visitor')
    qs = visitor_model.objects.all()
    qs.filter(user__isnull=False).select_for_update().update(email='')


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0005_changed_user_on_delete'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
