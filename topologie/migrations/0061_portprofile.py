# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-26 16:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


def transfer_profil(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    port = apps.get_model("topologie", "Port")
    profil = apps.get_model("topologie", "PortProfile")
    vlan = apps.get_model("machines", "Vlan")
    port_list = port.objects.using(db_alias).all()
    profil_nothing = profil.objects.using(db_alias).create(
        name="nothing", profil_default="nothing", radius_type="NO"
    )
    profil_uplink = profil.objects.using(db_alias).create(
        name="uplink", profil_default="uplink", radius_type="NO"
    )
    profil_machine = profil.objects.using(db_alias).create(
        name="asso_machine", profil_default="asso_machine", radius_type="NO"
    )
    profil_room = profil.objects.using(db_alias).create(
        name="room", profil_default="room", radius_type="NO"
    )
    profil_borne = profil.objects.using(db_alias).create(
        name="accesspoint", profil_default="accesspoint", radius_type="NO"
    )
    for vlan_instance in vlan.objects.using(db_alias).all():
        if port.objects.using(db_alias).filter(vlan_force=vlan_instance):
            custom_profile = profil.objects.using(db_alias).create(
                name="vlan-force-" + str(vlan_instance.vlan_id),
                radius_type="NO",
                vlan_untagged=vlan_instance,
            )
            port.objects.using(db_alias).filter(vlan_force=vlan_instance).update(
                custom_profile=custom_profile
            )
    if (
        port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="STRICT")
        .count()
        > port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="NO")
        .count()
        and port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="STRICT")
        .count()
        > port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="COMMON")
        .count()
    ):
        profil_room.radius_type = "MAC-radius"
        profil_room.radius_mode = "STRICT"
        common_profil = profil.objects.using(db_alias).create(
            name="mac-radius-common", radius_type="MAC-radius", radius_mode="COMMON"
        )
        no_rad_profil = profil.objects.using(db_alias).create(
            name="no-radius", radius_type="NO"
        )
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="COMMON"
        ).update(custom_profile=common_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="NO"
        ).update(custom_profile=no_rad_profil)
    elif (
        port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="COMMON")
        .count()
        > port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="NO")
        .count()
        and port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="COMMON")
        .count()
        > port.objects.using(db_alias)
        .filter(room__isnull=False)
        .filter(radius="STRICT")
        .count()
    ):
        profil_room.radius_type = "MAC-radius"
        profil_room.radius_mode = "COMMON"
        strict_profil = profil.objects.using(db_alias).create(
            name="mac-radius-strict", radius_type="MAC-radius", radius_mode="STRICT"
        )
        no_rad_profil = profil.objects.using(db_alias).create(
            name="no-radius", radius_type="NO"
        )
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="STRICT"
        ).update(custom_profile=strict_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="NO"
        ).update(custom_profile=no_rad_profil)
    else:
        strict_profil = profil.objects.using(db_alias).create(
            name="mac-radius-strict", radius_type="MAC-radius", radius_mode="STRICT"
        )
        common_profil = profil.objects.using(db_alias).create(
            name="mac-radius-common", radius_type="MAC-radius", radius_mode="COMMON"
        )
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="STRICT"
        ).update(custom_profile=strict_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius="NO"
        ).update(custom_profile=common_profil)
    profil_room.save()


class Migration(migrations.Migration):

    dependencies = [
        ("machines", "0082_auto_20180525_2209"),
        ("topologie", "0060_server"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "profil_default",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("room", "room"),
                            ("accespoint", "accesspoint"),
                            ("uplink", "uplink"),
                            ("asso_machine", "asso_machine"),
                            ("nothing", "nothing"),
                        ],
                        max_length=32,
                        null=True,
                        unique=True,
                        verbose_name="profil default",
                    ),
                ),
                (
                    "radius_type",
                    models.CharField(
                        choices=[
                            ("NO", "NO"),
                            ("802.1X", "802.1X"),
                            ("MAC-radius", "MAC-radius"),
                        ],
                        help_text="Type of radius auth : inactive, mac-address or 802.1X",
                        max_length=32,
                        verbose_name="RADIUS type",
                    ),
                ),
                (
                    "radius_mode",
                    models.CharField(
                        choices=[("STRICT", "STRICT"), ("COMMON", "COMMON")],
                        default="COMMON",
                        help_text="In case of mac-auth : mode common or strict on this port",
                        max_length=32,
                        verbose_name="RADIUS mode",
                    ),
                ),
                (
                    "speed",
                    models.CharField(
                        choices=[
                            ("10-half", "10-half"),
                            ("100-half", "100-half"),
                            ("10-full", "10-full"),
                            ("100-full", "100-full"),
                            ("1000-full", "1000-full"),
                            ("auto", "auto"),
                            ("auto-10", "auto-10"),
                            ("auto-100", "auto-100"),
                        ],
                        default="auto",
                        help_text="Port speed limit",
                        max_length=32,
                        verbose_name="Speed",
                    ),
                ),
                (
                    "mac_limit",
                    models.IntegerField(
                        blank=True,
                        help_text="Limit of mac-address on this port",
                        null=True,
                        verbose_name="Mac limit",
                    ),
                ),
                (
                    "flow_control",
                    models.BooleanField(
                        default=False,
                        help_text="Flow control",
                        verbose_name="Flow control",
                    ),
                ),
                (
                    "dhcp_snooping",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue dhcp",
                        verbose_name="Dhcp snooping",
                    ),
                ),
                (
                    "dhcpv6_snooping",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue dhcpv6",
                        verbose_name="Dhcpv6 snooping",
                    ),
                ),
                (
                    "arp_protect",
                    models.BooleanField(
                        default=False,
                        help_text="Check if ip is dhcp assigned",
                        verbose_name="Arp protect",
                    ),
                ),
                (
                    "ra_guard",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue ra",
                        verbose_name="Ra guard",
                    ),
                ),
                (
                    "loop_protect",
                    models.BooleanField(
                        default=False,
                        help_text="Protect again loop",
                        verbose_name="Loop Protect",
                    ),
                ),
                (
                    "vlan_tagged",
                    models.ManyToManyField(
                        blank=True,
                        related_name="vlan_tagged",
                        to="machines.Vlan",
                        verbose_name="VLAN(s) tagged",
                    ),
                ),
                (
                    "vlan_untagged",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vlan_untagged",
                        to="machines.Vlan",
                        verbose_name="VLAN untagged",
                    ),
                ),
            ],
            options={
                "verbose_name": "Port profile",
                "permissions": (
                    ("view_port_profile", "Can view a port profile object"),
                ),
                "verbose_name_plural": "Port profiles",
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.AddField(
            model_name="port",
            name="custom_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="topologie.PortProfile",
            ),
        ),
        migrations.RunPython(transfer_profil),
        migrations.RemoveField(model_name="port", name="radius"),
        migrations.RemoveField(model_name="port", name="vlan_force"),
        migrations.AddField(
            model_name="port",
            name="state",
            field=models.BooleanField(
                default=True,
                help_text="Port state Active",
                verbose_name="Port State Active",
            ),
        ),
    ]
