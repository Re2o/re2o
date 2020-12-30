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
    dependencies = [("machines", "0001_squashed_0108")]
    replaces = [
        ("topologie", "0001_initial"),
        ("topologie", "0002_auto_20160703_1118"),
        ("topologie", "0003_room"),
        ("topologie", "0004_auto_20160703_1122"),
        ("topologie", "0005_auto_20160703_1123"),
        ("topologie", "0006_auto_20160703_1129"),
        ("topologie", "0007_auto_20160703_1148"),
        ("topologie", "0008_port_room"),
        ("topologie", "0009_auto_20160703_1200"),
        ("topologie", "0010_auto_20160704_2148"),
        ("topologie", "0011_auto_20160704_2153"),
        ("topologie", "0012_port_machine_interface"),
        ("topologie", "0013_port_related"),
        ("topologie", "0014_auto_20160706_1238"),
        ("topologie", "0015_auto_20160706_1452"),
        ("topologie", "0016_auto_20160706_1531"),
        ("topologie", "0017_auto_20160718_1141"),
        ("topologie", "0018_room_details"),
        ("topologie", "0019_auto_20161026_1348"),
        ("topologie", "0020_auto_20161119_0033"),
        ("topologie", "0021_port_radius"),
        ("topologie", "0022_auto_20161211_1622"),
        ("topologie", "0023_auto_20170817_1654"),
        ("topologie", "0023_auto_20170826_1530"),
        ("topologie", "0024_auto_20170818_1021"),
        ("topologie", "0024_auto_20170826_1800"),
        ("topologie", "0025_merge_20170902_1242"),
        ("topologie", "0026_auto_20170902_1245"),
        ("topologie", "0027_auto_20170905_1442"),
        ("topologie", "0028_auto_20170913_1503"),
        ("topologie", "0029_auto_20171002_0334"),
        ("topologie", "0030_auto_20171004_0235"),
        ("topologie", "0031_auto_20171015_2033"),
        ("topologie", "0032_auto_20171026_0338"),
        ("topologie", "0033_auto_20171231_1743"),
        ("topologie", "0034_borne"),
        ("topologie", "0035_auto_20180324_0023"),
        ("topologie", "0036_transferborne"),
        ("topologie", "0037_auto_20180325_0127"),
        ("topologie", "0038_transfersw"),
        ("topologie", "0039_port_new_switch"),
        ("topologie", "0040_transferports"),
        ("topologie", "0041_transferportsw"),
        ("topologie", "0042_transferswitch"),
        ("topologie", "0043_renamenewswitch"),
        ("topologie", "0044_auto_20180326_0002"),
        ("topologie", "0045_auto_20180326_0123"),
        ("topologie", "0046_auto_20180326_0129"),
        ("topologie", "0047_ap_machine"),
        ("topologie", "0048_ap_machine"),
        ("topologie", "0049_switchs_machine"),
        ("topologie", "0050_port_new_switch"),
        ("topologie", "0051_switchs_machine"),
        ("topologie", "0052_transferports"),
        ("topologie", "0053_finalsw"),
        ("topologie", "0054_auto_20180326_1742"),
        ("topologie", "0055_auto_20180329_0431"),
        ("topologie", "0056_building_switchbay"),
        ("topologie", "0057_auto_20180408_0316"),
        ("topologie", "0058_remove_switch_location"),
        ("topologie", "0059_auto_20180415_2249"),
        ("topologie", "0060_server"),
        ("topologie", "0061_portprofile"),
        ("topologie", "0062_auto_20180815_1918"),
        ("topologie", "0063_auto_20180919_2225"),
        ("topologie", "0064_switch_automatic_provision"),
        ("topologie", "0065_auto_20180927_1836"),
        ("topologie", "0066_modelswitch_commercial_name"),
        ("topologie", "0067_auto_20181230_1819"),
        ("topologie", "0068_auto_20190102_1758"),
        ("topologie", "0069_auto_20190108_1439"),
        ("topologie", "0070_auto_20190218_1743"),
        ("topologie", "0071_auto_20190218_1936"),
        ("topologie", "0072_auto_20190720_2318"),
        ("topologie", "0073_auto_20191120_0159"),
        ("topologie", "0074_auto_20200419_1640"),
    ]
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
                "verbose_name_plural": "port",
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
    ]
