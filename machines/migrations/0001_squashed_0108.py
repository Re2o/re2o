# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import macaddress.fields
import re2o.mixins
import re2o.field_permissions
import datetime


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    replaces = [
        ("machines", "0001_initial"),
        ("machines", "0001_squashed_0108"),
        ("machines", "0002_auto_20160703_1444"),
        ("machines", "0003_auto_20160703_1450"),
        ("machines", "0004_auto_20160703_1451"),
        ("machines", "0005_auto_20160703_1523"),
        ("machines", "0006_auto_20160703_1813"),
        ("machines", "0007_auto_20160703_1816"),
        ("machines", "0008_remove_interface_ipv6"),
        ("machines", "0009_auto_20160703_2358"),
        ("machines", "0010_auto_20160704_0104"),
        ("machines", "0011_auto_20160704_0105"),
        ("machines", "0012_auto_20160704_0118"),
        ("machines", "0013_auto_20160705_1014"),
        ("machines", "0014_auto_20160706_1220"),
        ("machines", "0015_auto_20160707_0105"),
        ("machines", "0016_auto_20160708_1633"),
        ("machines", "0017_auto_20160708_1645"),
        ("machines", "0018_auto_20160708_1813"),
        ("machines", "0019_auto_20160718_1141"),
        ("machines", "0020_auto_20160718_1849"),
        ("machines", "0021_auto_20161006_1943"),
        ("machines", "0022_auto_20161011_1829"),
        ("machines", "0023_iplist_ip_type"),
        ("machines", "0024_machinetype_need_infra"),
        ("machines", "0025_auto_20161023_0038"),
        ("machines", "0026_auto_20161026_1348"),
        ("machines", "0027_alias"),
        ("machines", "0028_iptype_domaine_ip"),
        ("machines", "0029_iptype_domaine_range"),
        ("machines", "0030_auto_20161118_1730"),
        ("machines", "0031_auto_20161119_1709"),
        ("machines", "0032_auto_20161119_1850"),
        ("machines", "0033_extension_need_infra"),
        ("machines", "0034_iplist_need_infra"),
        ("machines", "0035_auto_20161224_1201"),
        ("machines", "0036_auto_20161224_1204"),
        ("machines", "0037_domain_cname"),
        ("machines", "0038_auto_20161224_1721"),
        ("machines", "0039_auto_20161224_1732"),
        ("machines", "0040_remove_interface_dns"),
        ("machines", "0041_remove_ns_interface"),
        ("machines", "0042_ns_ns"),
        ("machines", "0043_auto_20170721_0350"),
        ("machines", "0044_auto_20170808_0233"),
        ("machines", "0045_auto_20170808_0348"),
        ("machines", "0046_auto_20170808_1423"),
        ("machines", "0047_auto_20170809_0606"),
        ("machines", "0048_auto_20170823_2315"),
        ("machines", "0049_vlan"),
        ("machines", "0050_auto_20170826_0022"),
        ("machines", "0051_iptype_vlan"),
        ("machines", "0052_auto_20170828_2322"),
        ("machines", "0053_text"),
        ("machines", "0054_text_zone"),
        ("machines", "0055_nas"),
        ("machines", "0056_nas_port_access_mode"),
        ("machines", "0057_nas_autocapture_mac"),
        ("machines", "0058_auto_20171002_0350"),
        ("machines", "0059_iptype_prefix_v6"),
        ("machines", "0060_iptype_ouverture_ports"),
        ("machines", "0061_auto_20171015_2033"),
        ("machines", "0062_extension_origin_v6"),
        ("machines", "0063_auto_20171020_0040"),
        ("machines", "0064_auto_20171115_0253"),
        ("machines", "0065_auto_20171115_1514"),
        ("machines", "0066_srv"),
        ("machines", "0067_auto_20171116_0152"),
        ("machines", "0068_auto_20171116_0252"),
        ("machines", "0069_auto_20171116_0822"),
        ("machines", "0070_auto_20171231_1947"),
        ("machines", "0071_auto_20171231_2100"),
        ("machines", "0072_auto_20180108_1822"),
        ("machines", "0073_auto_20180128_2203"),
        ("machines", "0074_auto_20180129_0352"),
        ("machines", "0075_auto_20180130_0052"),
        ("machines", "0076_auto_20180130_1623"),
        ("machines", "0077_auto_20180409_2243"),
        ("machines", "0078_auto_20180415_1252"),
        ("machines", "0079_auto_20180416_0107"),
        ("machines", "0080_auto_20180502_2334"),
        ("machines", "0081_auto_20180521_1413"),
        ("machines", "0082_auto_20180525_2209"),
        ("machines", "0083_remove_duplicate_rights"),
        ("machines", "0084_dname"),
        ("machines", "0085_sshfingerprint"),
        ("machines", "0086_role"),
        ("machines", "0087_dnssec"),
        ("machines", "0088_iptype_prefix_v6_length"),
        ("machines", "0089_auto_20180805_1148"),
        ("machines", "0090_auto_20180805_1459"),
        ("machines", "0091_auto_20180806_2310"),
        ("machines", "0092_auto_20180807_0926"),
        ("machines", "0093_auto_20180807_1115"),
        ("machines", "0094_auto_20180815_1918"),
        ("machines", "0095_auto_20180919_2225"),
        ("machines", "0096_auto_20181013_1417"),
        ("machines", "0097_extension_dnssec"),
        ("machines", "0098_auto_20190102_1745"),
        ("machines", "0099_role_recursive_dns"),
        ("machines", "0100_auto_20190102_1753"),
        ("machines", "0101_auto_20190108_1623"),
        ("machines", "0102_auto_20190303_1611"),
        ("machines", "0103_auto_20191002_2222"),
        ("machines", "0104_auto_20191002_2231"),
        ("machines", "0105_dname_ttl"),
        ("machines", "0106_auto_20191120_0159"),
        ("machines", "0107_fix_lowercase_domain"),
        ("machines", "0108_ipv6list_active"),
    ]
    operations = [
        migrations.CreateModel(
            name="Machine",
            bases=(
                re2o.mixins.RevMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
                re2o.mixins.AclMixin,
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
                    "name",
                    models.CharField(
                        max_length=255, help_text="Optional.", blank=True, null=True
                    ),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "permissions": (
                    ("view_machine", "Can view a machine object"),
                    ("change_machine_user", "Can change the user of a machine"),
                ),
                "verbose_name": "machine",
                "verbose_name_plural": "machines",
            },
        ),
        migrations.CreateModel(
            name="MachineType",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    ("view_machinetype", "Can view a machine type object"),
                    ("use_all_machinetype", "Can use all machine types"),
                ),
                "verbose_name": "machine type",
                "verbose_name_plural": "machine types",
            },
        ),
        migrations.CreateModel(
            name="IpType",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("need_infra", models.BooleanField(default=False)),
                ("domaine_ip_start", models.GenericIPAddressField(protocol="IPv4")),
                ("domaine_ip_stop", models.GenericIPAddressField(protocol="IPv4")),
                (
                    "domaine_ip_network",
                    models.GenericIPAddressField(
                        protocol="IPv4",
                        null=True,
                        blank=True,
                        help_text="Network containing the domain's IPv4 range optional).",
                    ),
                ),
                (
                    "domaine_ip_netmask",
                    models.IntegerField(
                        default=24,
                        validators=[
                            django.core.validators.MaxValueValidator(31),
                            django.core.validators.MinValueValidator(8),
                        ],
                        help_text="Netmask for the domain's IPv4 range.",
                    ),
                ),
                (
                    "reverse_v4",
                    models.BooleanField(
                        default=False, help_text="Enable reverse DNS for IPv4."
                    ),
                ),
                (
                    "prefix_v6",
                    models.GenericIPAddressField(
                        protocol="IPv6", null=True, blank=True
                    ),
                ),
                (
                    "prefix_v6_length",
                    models.IntegerField(
                        default=64,
                        validators=[
                            django.core.validators.MaxValueValidator(128),
                            django.core.validators.MinValueValidator(0),
                        ],
                    ),
                ),
                (
                    "reverse_v6",
                    models.BooleanField(
                        default=False, help_text="Enable reverse DNS for IPv6."
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_iptype", "Can view an IP type object"),
                    ("use_all_iptype", "Can use all IP types"),
                ),
                "verbose_name": "Ip type",
                "verbose_name_plural": "Ip types",
            },
        ),
        migrations.CreateModel(
            name="Vlan",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "vlan_id",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MaxValueValidator(4095)]
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("comment", models.CharField(max_length=256, blank=True)),
                ("arp_protect", models.BooleanField(default=False)),
                ("dhcp_snooping", models.BooleanField(default=False)),
                ("dhcpv6_snooping", models.BooleanField(default=False)),
                (
                    "igmp",
                    models.BooleanField(
                        default=False, help_text="v4 multicast management."
                    ),
                ),
                (
                    "mld",
                    models.BooleanField(
                        default=False, help_text="v6 multicast management."
                    ),
                ),
            ],
            options={
                "permissions": (("view_vlan", "Can view a VLAN object"),),
                "verbose_name": "VLAN",
                "verbose_name_plural": "VLANs",
            },
        ),
        migrations.CreateModel(
            name="Nas",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "port_access_mode",
                    models.CharField(
                        choices=(("802.1X", "802.1X"), ("Mac-address", "MAC-address")),
                        default="802.1X",
                        max_length=32,
                    ),
                ),
                ("autocapture_mac", models.BooleanField(default=False)),
            ],
            options={
                "permissions": (("view_nas", "Can view a NAS device object"),),
                "verbose_name": "NAS device",
                "verbose_name_plural": "NAS devices",
            },
        ),
        migrations.CreateModel(
            name="SOA",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                (
                    "mail",
                    models.EmailField(help_text="Contact email address for the zone."),
                ),
                (
                    "refresh",
                    models.PositiveIntegerField(
                        default=86400,
                        help_text="Seconds before the secondary DNS have to ask the primary DNS serial to detect a modification.",
                    ),
                ),
                (
                    "retry",
                    models.PositiveIntegerField(
                        default=7200,
                        help_text="Seconds before the secondary DNS ask the serial again in case of a primary DNS timeout.",
                    ),
                ),
                (
                    "expire",
                    models.PositiveIntegerField(
                        default=3600000,
                        help_text="Seconds before the secondary DNS stop answering requests in case of primary DNS timeout.",
                    ),
                ),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        default=172800, help_text="Time To Live."
                    ),
                ),
            ],
            options={
                "permissions": (("view_soa", "Can view an SOA record object"),),
                "verbose_name": "SOA record",
                "verbose_name_plural": "SOA records",
            },
        ),
        migrations.CreateModel(
            name="Extension",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "name",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        help_text="Zone name, must begin with a dot (.example.org).",
                    ),
                ),
                ("need_infra", models.BooleanField(default=False)),
                (
                    "origin_v6",
                    models.GenericIPAddressField(
                        protocol="IPv6",
                        null=True,
                        blank=True,
                        help_text="AAAA record associated with the zone.",
                    ),
                ),
                (
                    "dnssec",
                    models.BooleanField(
                        default=False,
                        help_text="Should the zone be signed with DNSSEC.",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_extension", "Can view an extension object"),
                    ("use_all_extension", "Can use all extensions"),
                ),
                "verbose_name": "DNS extension",
                "verbose_name_plural": "DNS extensions",
            },
        ),
        migrations.CreateModel(
            name="Mx",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("priority", models.PositiveIntegerField()),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        verbose_name="Time To Live (TTL)", default=172800
                    ),
                ),
            ],
            options={
                "permissions": (("view_mx", "Can view an MX record object"),),
                "verbose_name": "MX record",
                "verbose_name_plural": "MX records",
            },
        ),
        migrations.CreateModel(
            name="Ns",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "ttl",
                    models.PositiveIntegerField(
                        verbose_name="Time To Live (TTL)", default=172800
                    ),
                ),
            ],
            options={
                "permissions": (("view_ns", "Can view an NS record object"),),
                "verbose_name": "NS record",
                "verbose_name_plural": "NS records",
            },
        ),
        migrations.CreateModel(
            name="Txt",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("field1", models.CharField(max_length=255)),
                ("field2", models.TextField(max_length=2047)),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        verbose_name="Time To Live (TTL)", default=172800
                    ),
                ),
            ],
            options={
                "permissions": (("view_txt", "Can view a TXT record object"),),
                "verbose_name": "TXT record",
                "verbose_name_plural": "TXT records",
            },
        ),
        migrations.CreateModel(
            name="DName",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("alias", models.CharField(max_length=255)),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        verbose_name="Time To Live (TTL)", default=172800
                    ),
                ),
            ],
            options={
                "permissions": (("view_dname", "Can view a DNAME record object"),),
                "verbose_name": "DNAME record",
                "verbose_name_plural": "DNAME records",
            },
        ),
        migrations.CreateModel(
            name="Srv",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("service", models.CharField(max_length=31)),
                (
                    "protocole",
                    models.CharField(
                        max_length=3,
                        choices=(("TCP", "TCP"), ("UDP", "UDP")),
                        default="TCP",
                    ),
                ),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        default=172800, help_text="Time To Live."
                    ),
                ),
                (
                    "priority",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(65535)],
                        help_text="Priority of the target server (positive integer value, the lower it is, the more the server will be used if available).",
                    ),
                ),
                (
                    "weight",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(65535)],
                        help_text="Relative weight for records with the same priority (integer value between 0 and 65535).",
                    ),
                ),
                (
                    "port",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MaxValueValidator(65535)],
                        help_text="TCP/UDP port.",
                    ),
                ),
            ],
            options={
                "permissions": (("view_srv", "Can view an SRV record object"),),
                "verbose_name": "SRV record",
                "verbose_name_plural": "SRV records",
            },
        ),
        migrations.CreateModel(
            name="SshFp",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "pub_key_entry",
                    models.TextField(help_text="SSH public key.", max_length=2048),
                ),
                (
                    "algo",
                    models.CharField(
                        choices=(
                            ("ssh-rsa", "ssh-rsa"),
                            ("ssh-ed25519", "ssh-ed25519"),
                            ("ecdsa-sha2-nistp256", "ecdsa-sha2-nistp256"),
                            ("ecdsa-sha2-nistp384", "ecdsa-sha2-nistp384"),
                            ("ecdsa-sha2-nistp521", "ecdsa-sha2-nistp521"),
                        ),
                        max_length=32,
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        help_text="Comment.", max_length=255, null=True, blank=True
                    ),
                ),
            ],
            options={
                "permissions": (("view_sshfp", "Can view an SSHFP record object"),),
                "verbose_name": "SSHFP record",
                "verbose_name_plural": "SSHFP records",
            },
        ),
        migrations.CreateModel(
            name="Interface",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
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
                ("mac_address", macaddress.fields.MACAddressField(integer=False)),
                ("details", models.CharField(max_length=255, blank=True)),
            ],
            options={
                "permissions": (
                    ("view_interface", "Can view an interface object"),
                    (
                        "change_interface_machine",
                        "Can change the owner of an interface",
                    ),
                ),
                "verbose_name": "interface",
                "verbose_name_plural": "interfaces",
            },
        ),
        migrations.CreateModel(
            name="Ipv6List",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
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
                ("ipv6", models.GenericIPAddressField(protocol="IPv6")),
                ("slaac_ip", models.BooleanField(default=False)),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="If false,the DNS will not provide this ip.",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_ipv6list", "Can view an IPv6 addresses list object"),
                    (
                        "change_ipv6list_slaac_ip",
                        "Can change the SLAAC value of an IPv6 addresses list",
                    ),
                ),
                "verbose_name": "IPv6 addresses list",
                "verbose_name_plural": "IPv6 addresses lists",
            },
        ),
        migrations.CreateModel(
            name="Domain",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
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
                    "name",
                    models.CharField(
                        help_text="Mandatory and unique, must not contain dots.",
                        max_length=255,
                    ),
                ),
                (
                    "cname",
                    models.ForeignKey(
                        "self", null=True, blank=True, related_name="related_domain"
                    ),
                ),
                (
                    "ttl",
                    models.PositiveIntegerField(
                        verbose_name="Time To Live (TTL)", default=0
                    ),
                ),
            ],
            options={
                "unique_together": (("name", "extension"),),
                "permissions": (
                    ("view_domain", "Can view a domain object"),
                    ("change_ttl", "Can change the TTL of a domain object"),
                ),
                "verbose_name": "domain",
                "verbose_name_plural": "domains",
            },
        ),
        migrations.CreateModel(
            name="IpList",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("ipv4", models.GenericIPAddressField(protocol="IPv4", unique=True)),
            ],
            options={
                "permissions": (
                    ("view_iplist", "Can view an IPv4 addresses list object"),
                ),
                "verbose_name": "IPv4 addresses list",
                "verbose_name_plural": "IPv4 addresses lists",
            },
        ),
        migrations.CreateModel(
            name="Role",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("role_type", models.CharField(max_length=255, unique=True)),
                (
                    "specific_role",
                    models.CharField(
                        choices=(
                            ("dhcp-server", "DHCP server"),
                            ("switch-conf-server", "Switches configuration server"),
                            ("dns-recursive-server", "Recursive DNS server"),
                            ("ntp-server", "NTP server"),
                            ("radius-server", "RADIUS server"),
                            ("log-server", "Log server"),
                            ("ldap-master-server", "LDAP master server"),
                            ("ldap-backup-server", "LDAP backup server"),
                            ("smtp-server", "SMTP server"),
                            ("postgresql-server", "postgreSQL server"),
                            ("mysql-server", "mySQL server"),
                            ("sql-client", "SQL client"),
                            ("gateway", "Gateway"),
                        ),
                        null=True,
                        blank=True,
                        max_length=32,
                    ),
                ),
            ],
            options={
                "permissions": (("view_role", "Can view a role object"),),
                "verbose_name": "server role",
                "verbose_name_plural": "server roles",
            },
        ),
        migrations.CreateModel(
            name="Service",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "service_type",
                    models.CharField(max_length=255, blank=True, unique=True),
                ),
                (
                    "min_time_regen",
                    models.DurationField(
                        default=datetime.timedelta(minutes=1),
                        help_text="Minimal time before regeneration of the service.",
                    ),
                ),
                (
                    "regular_time_regen",
                    models.DurationField(
                        default=datetime.timedelta(hours=1),
                        help_text="Maximal time before regeneration of the service.",
                    ),
                ),
            ],
            options={
                "permissions": (("view_service", "Can view a service object"),),
                "verbose_name": "service to generate (DHCP, DNS, ...)",
                "verbose_name_plural": "services to generate (DHCP, DNS, ...)",
            },
        ),
        migrations.CreateModel(
            name="Service_link",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                ("last_regen", models.DateTimeField(auto_now_add=True)),
                ("asked_regen", models.BooleanField(default=False)),
            ],
            options={
                "permissions": (
                    ("view_service_link", "Can view a service server link object"),
                ),
                "verbose_name": "link between service and server",
                "verbose_name_plural": "links between service and server",
            },
        ),
        migrations.CreateModel(
            name="OuverturePortList",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "name",
                    models.CharField(
                        help_text="Name of the ports configuration", max_length=255
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "view_ouvertureportlist",
                        "Can view a ports opening list" " object",
                    ),
                ),
                "verbose_name": "ports opening list",
                "verbose_name_plural": "ports opening lists",
            },
        ),
        migrations.CreateModel(
            name="OuverturePort",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
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
                    "begin",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MaxValueValidator(65535)]
                    ),
                ),
                (
                    "end",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MaxValueValidator(65535)]
                    ),
                ),
                (
                    "protocole",
                    models.CharField(
                        max_length=1, choices=(("T", "TCP"), ("U", "UDP")), default="T"
                    ),
                ),
                (
                    "io",
                    models.CharField(
                        max_length=1, choices=(("I", "IN"), ("O", "OUT")), default="O"
                    ),
                ),
            ],
            options={
                "verbose_name": "ports opening",
                "verbose_name_plural": "ports openings",
            },
        ),
    ]
