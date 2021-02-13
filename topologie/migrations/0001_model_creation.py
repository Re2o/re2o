# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
import re2o.mixins
import re2o.field_permissions


class Migration(migrations.Migration):
    initial = True
    dependencies = [("machines", "0001_model_creation")]
    operations = [
        migrations.CreateModel(
            name="Stack",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=32, blank=True, null=True)),
                ("stack_id", models.CharField(max_length=32, unique=True)),
                ("details", models.CharField(max_length=255, blank=True, null=True)),
                ("member_id_min", models.PositiveIntegerField()),
                ("member_id_max", models.PositiveIntegerField()),
            ],
            options={
                "permissions": (("view_stack", "Can view a stack object"),),
                "verbose_name": "switches stack",
                "verbose_name_plural": "switches stacks",
            },
        ),
        migrations.CreateModel(
            name="AccessPoint",
            bases=("machines.machine",),
            fields=[
                (
                    "machine_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="machines.Machine",
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        max_length=255,
                        help_text="Details about the AP's location.",
                        blank=True,
                        null=True,
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_accesspoint", "Can view an access point object"),
                ),
                "verbose_name": "access point",
                "verbose_name_plural": "access points",
            },
        ),
        migrations.CreateModel(
            name="Server",
            bases=("machines.machine",),
            fields=[],
            options={"proxy": True},
        ),
        migrations.CreateModel(
            name="Switch",
            bases=("machines.machine",),
            fields=[
                (
                    "machine_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="machines.Machine",
                    ),
                ),
                ("number", models.PositiveIntegerField(help_text="Number of ports.")),
                ("stack_member_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "automatic_provision",
                    models.BooleanField(
                        default=False, help_text="Automatic provision for the switch."
                    ),
                ),
            ],
            options={
                "permissions": (("view_switch", "Can view a switch object"),),
                "verbose_name": "switch",
                "verbose_name_plural": "switches",
            },
        ),
        migrations.CreateModel(
            name="ModelSwitch",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("reference", models.CharField(max_length=255)),
                (
                    "commercial_name",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("firmware", models.CharField(max_length=255, null=True, blank=True)),
                (
                    "is_modular",
                    models.BooleanField(
                        default=False, help_text="The switch model is modular."
                    ),
                ),
                (
                    "is_itself_module",
                    models.BooleanField(
                        default=False, help_text="The switch is considered as a module."
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_modelswitch", "Can view a switch model object"),
                ),
                "verbose_name": "switch model",
                "verbose_name_plural": "switch models",
            },
        ),
        migrations.CreateModel(
            name="ModuleSwitch",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "reference",
                    models.CharField(
                        max_length=255,
                        help_text="Reference of a module.",
                        verbose_name="module reference",
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        max_length=255,
                        null=True,
                        blank=True,
                        help_text="Comment.",
                        verbose_name="comment",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_moduleswitch", "Can view a switch module object"),
                ),
                "verbose_name": "switch module",
                "verbose_name_plural": "switch modules",
            },
        ),
        migrations.CreateModel(
            name="ModuleOnSwitch",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "slot",
                    models.CharField(
                        max_length=15, help_text="Slot on switch.", verbose_name="slot"
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "view_moduleonswitch",
                        "Can view a link between switch and module object",
                    ),
                ),
                "verbose_name": "link between switch and module",
                "verbose_name_plural": "links between switch and module",
            },
        ),
        migrations.CreateModel(
            name="ConstructorSwitch",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "permissions": (
                    ("view_constructorswitch", "Can view a switch constructor object"),
                ),
                "verbose_name": "switch constructor",
                "verbose_name_plural": "switch constructors",
            },
        ),
        migrations.CreateModel(
            name="SwitchBay",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("info", models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                "permissions": (("view_switchbay", "Can view a switch bay object"),),
                "verbose_name": "switch bay",
                "verbose_name_plural": "switch bays",
            },
        ),
        migrations.CreateModel(
            name="Dormitory",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "permissions": (("view_dormitory", "Can view a dormitory object"),),
                "verbose_name": "dormitory",
                "verbose_name_plural": "dormitories",
            },
        ),
        migrations.CreateModel(
            name="Building",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "permissions": (("view_building", "Can view a building object"),),
                "verbose_name": "building",
                "verbose_name_plural": "buildings",
            },
        ),
        migrations.CreateModel(
            name="Port",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("port", models.PositiveIntegerField()),
                (
                    "state",
                    models.BooleanField(
                        default=True,
                        help_text="Port state Active.",
                        verbose_name="port state Active",
                    ),
                ),
                ("details", models.CharField(max_length=255, blank=True)),
            ],
            options={
                "permissions": (("view_port", "Can view a port object"),),
                "verbose_name": "port",
                "verbose_name_plural": "ports",
            },
        ),
        migrations.CreateModel(
            name="PortProfile",
            bases=(
                re2o.mixins.AclMixin,
                re2o.mixins.RevMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "profil_default",
                    models.CharField(
                        max_length=32,
                        choices=(
                            ("room", "Room"),
                            ("access_point", "Access point"),
                            ("uplink", "Uplink"),
                            ("asso_machine", "Organisation machine"),
                            ("nothing", "Nothing"),
                        ),
                        blank=True,
                        null=True,
                        verbose_name="default profile",
                    ),
                ),
                (
                    "radius_type",
                    models.CharField(
                        max_length=32,
                        choices=(
                            ("NO", "NO"),
                            ("802.1X", "802.1X"),
                            ("MAC-radius", "MAC-RADIUS"),
                        ),
                        help_text="Type of RADIUS authentication: inactive, MAC-address or 802.1X.",
                        verbose_name="RADIUS type",
                    ),
                ),
                (
                    "radius_mode",
                    models.CharField(
                        max_length=32,
                        choices=(("STRICT", "STRICT"), ("COMMON", "COMMON")),
                        default="COMMON",
                        help_text="In case of MAC-authentication: mode COMMON or STRICT on this port.",
                        verbose_name="RADIUS mode",
                    ),
                ),
                (
                    "speed",
                    models.CharField(
                        max_length=32,
                        choices=(
                            ("10-half", "10-half"),
                            ("100-half", "100-half"),
                            ("10-full", "10-full"),
                            ("100-full", "100-full"),
                            ("1000-full", "1000-full"),
                            ("auto", "auto"),
                            ("auto-10", "auto-10"),
                            ("auto-100", "auto-100"),
                        ),
                        default="auto",
                        help_text="Port speed limit.",
                    ),
                ),
                (
                    "mac_limit",
                    models.IntegerField(
                        null=True,
                        blank=True,
                        help_text="Limit of MAC-address on this port.",
                        verbose_name="MAC limit",
                    ),
                ),
                (
                    "flow_control",
                    models.BooleanField(default=False, help_text="Flow control."),
                ),
                (
                    "dhcp_snooping",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue DHCP.",
                        verbose_name="DHCP snooping",
                    ),
                ),
                (
                    "dhcpv6_snooping",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue DHCPv6.",
                        verbose_name="DHCPv6 snooping",
                    ),
                ),
                (
                    "arp_protect",
                    models.BooleanField(
                        default=False,
                        help_text="Check if IP address is DHCP assigned.",
                        verbose_name="ARP protection",
                    ),
                ),
                (
                    "ra_guard",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against rogue RA.",
                        verbose_name="RA guard",
                    ),
                ),
                (
                    "loop_protect",
                    models.BooleanField(
                        default=False,
                        help_text="Protect against loop.",
                        verbose_name="loop protection",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_portprofile", "Can view a port profile object"),
                ),
                "verbose_name": "port profile",
                "verbose_name_plural": "port profiles",
            },
        ),
        migrations.CreateModel(
            name="Room",
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
                ("name", models.CharField(max_length=255)),
                ("details", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "verbose_name": "room",
                "verbose_name_plural": "rooms",
                "ordering": ["building__name"],
                "permissions": (("view_room", "Can view a room object"),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
    ]
