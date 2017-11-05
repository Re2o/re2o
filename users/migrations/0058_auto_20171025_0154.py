# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-24 23:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def create_move_room(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Adherent = apps.get_model('users', 'Adherent')
    Club = apps.get_model('users', 'Club')
    db_alias = schema_editor.connection.alias
    users = Adherent.objects.using(db_alias).all()
    clubs = Club.objects.using(db_alias).all()
    for user in users:
        user.room_adherent_id = user.room_id
        user.save(using=db_alias)
    for user in clubs:
        user.room_club_id = user.room_id
        user.save(using=db_alias)


def delete_move_room(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Adherent = apps.get_model('users', 'Adherent')
    Club = apps.get_model('users', 'Club')
    db_alias = schema_editor.connection.alias
    users = Adherent.objects.using(db_alias).all()
    clubs = Club.objects.using(db_alias).all()
    for user in users:
        user.room_id = user.room_adherent_id
        user.save(using=db_alias)
    for user in clubs:
        user.room_id = user.room_club_id
        user.save(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0031_auto_20171015_2033'),
        ('users', '0057_auto_20171023_0301'),
    ]

    operations = [
        migrations.AddField(
            model_name='adherent',
            name='room_adherent',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='topologie.Room'),
        ),
        migrations.AddField(
            model_name='club',
            name='room_club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='topologie.Room'),
        ),
        migrations.RunPython(create_move_room, delete_move_room),
        migrations.RemoveField(
            model_name='user',
            name='room',
        ),
    ]
