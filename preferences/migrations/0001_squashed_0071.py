# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import re2o.mixins
import re2o.aes_field


class Migration(migrations.Migration):
    dependencies = []
    replaces = [
        ("preferences", "0001_initial"),
        ("preferences", "0001_squashed_0071"),
        ("preferences", "0002_auto_20170625_1923"),
        ("preferences", "0003_optionaluser_solde_negatif"),
        ("preferences", "0004_assooption_services"),
        ("preferences", "0005_auto_20170824_0139"),
        ("preferences", "0006_auto_20170824_0143"),
        ("preferences", "0007_auto_20170824_2056"),
        ("preferences", "0008_auto_20170824_2122"),
        ("preferences", "0009_assooption_utilisateur_asso"),
        ("preferences", "0010_auto_20170825_0459"),
        ("preferences", "0011_auto_20170825_2307"),
        ("preferences", "0012_generaloption_req_expire_hrs"),
        ("preferences", "0013_generaloption_site_name"),
        ("preferences", "0014_generaloption_email_from"),
        ("preferences", "0015_optionaltopologie_radius_general_policy"),
        ("preferences", "0016_auto_20170902_1520"),
        ("preferences", "0017_mailmessageoption"),
        ("preferences", "0018_optionaltopologie_mac_autocapture"),
        ("preferences", "0019_remove_optionaltopologie_mac_autocapture"),
        ("preferences", "0020_optionalmachine_ipv6"),
        ("preferences", "0021_auto_20171015_1741"),
        ("preferences", "0022_auto_20171015_1758"),
        ("preferences", "0023_auto_20171015_2033"),
        ("preferences", "0024_optionaluser_all_can_create"),
        ("preferences", "0025_auto_20171231_2142"),
        ("preferences", "0025_generaloption_general_message"),
        ("preferences", "0026_auto_20171216_0401"),
        ("preferences", "0027_merge_20180106_2019"),
        ("preferences", "0028_assooption_description"),
        ("preferences", "0028_auto_20180111_1129"),
        ("preferences", "0028_auto_20180128_2203"),
        ("preferences", "0029_auto_20180111_1134"),
        ("preferences", "0029_auto_20180318_0213"),
        ("preferences", "0029_auto_20180318_1005"),
        ("preferences", "0030_auto_20180111_2346"),
        ("preferences", "0030_merge_20180320_1419"),
        ("preferences", "0031_auto_20180323_0218"),
        ("preferences", "0031_optionaluser_self_adhesion"),
        ("preferences", "0032_optionaluser_min_online_payment"),
        ("preferences", "0032_optionaluser_shell_default"),
        ("preferences", "0033_accueiloption"),
        ("preferences", "0033_generaloption_gtu_sum_up"),
        ("preferences", "0034_auto_20180114_2025"),
        ("preferences", "0034_auto_20180416_1120"),
        ("preferences", "0035_auto_20180114_2132"),
        ("preferences", "0035_optionaluser_allow_self_subscription"),
        ("preferences", "0036_auto_20180114_2141"),
        ("preferences", "0037_auto_20180114_2156"),
        ("preferences", "0038_auto_20180114_2209"),
        ("preferences", "0039_auto_20180115_0003"),
        ("preferences", "0040_auto_20180129_1745"),
        ("preferences", "0041_merge_20180130_0052"),
        ("preferences", "0042_auto_20180222_1743"),
        ("preferences", "0043_optionalmachine_create_machine"),
        ("preferences", "0044_remove_payment_pass"),
        ("preferences", "0045_remove_unused_payment_fields"),
        ("preferences", "0046_optionaluser_mail_extension"),
        ("preferences", "0047_mailcontact"),
        ("preferences", "0048_auto_20180811_1515"),
        ("preferences", "0049_optionaluser_self_change_shell"),
        ("preferences", "0050_auto_20180818_1329"),
        ("preferences", "0051_auto_20180919_2225"),
        ("preferences", "0052_optionaluser_delete_notyetactive"),
        ("preferences", "0053_optionaluser_self_change_room"),
        ("preferences", "0055_generaloption_main_site_url"),
        ("preferences", "0056_1_radiusoption"),
        ("preferences", "0056_2_radiusoption"),
        ("preferences", "0056_3_radiusoption"),
        ("preferences", "0056_4_radiusoption"),
        ("preferences", "0057_optionaluser_all_users_active"),
        ("preferences", "0058_auto_20190108_1650"),
        ("preferences", "0059_auto_20190120_1739"),
        ("preferences", "0060_auto_20190712_1821"),
        ("preferences", "0061_optionaluser_allow_archived_connexion"),
        ("preferences", "0062_auto_20190910_1909"),
        ("preferences", "0063_mandate"),
        ("preferences", "0064_auto_20191008_1335"),
        ("preferences", "0065_auto_20191010_1227"),
        ("preferences", "0066_optionalmachine_default_dns_ttl"),
        ("preferences", "0067_auto_20191120_0159"),
        ("preferences", "0068_optionaluser_allow_set_password_during_user_creation"),
        ("preferences", "0069_optionaluser_disable_emailnotyetconfirmed"),
        ("preferences", "0070_auto_20200419_0225"),
        ("preferences", "0071_optionaluser_self_change_pseudo"),
    ]
    operations = [
        migrations.CreateModel(
            name="OptionalUser",
            bases=(re2o.mixins.AclMixin, models.Model),
            options={
                "permissions": (("view_optionaluser", "Can view the user options"),),
                "verbose_name": "user options",
            },
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
                ("is_tel_mandatory", models.BooleanField(default=True)),
                ("gpg_fingerprint", models.BooleanField(default=True)),
                ("all_can_create_club", models.BooleanField(default=False)),
                ("all_can_create_adherent", models.BooleanField(default=False)),
                ("self_change_shell", models.BooleanField(default=False)),
                ("self_change_pseudo", models.BooleanField(default=True)),
                (
                    "self_room_policy",
                    models.CharField(
                        choices=[
                            ("DISABLED", "Users can't select their room"),
                            (
                                "ONLY_INACTIVE",
                                "Users can only select a room occupied by a user with a disabled connection.",
                            ),
                            ("ALL_ROOM", "Users can select all rooms"),
                        ],
                        default="DISABLED",
                        help_text="Policy on self users room edition",
                        max_length=32,
                    ),
                ),
                ("local_email_accounts_enabled", models.BooleanField(default=False)),
                (
                    "local_email_domain",
                    models.CharField(
                        default="@example.org",
                        help_text="Domain to use for local email accounts.",
                        max_length=32,
                    ),
                ),
                (
                    "max_email_address",
                    models.IntegerField(
                        default=15,
                        help_text="Maximum number of local email addresses for a standard user.",
                    ),
                ),
                (
                    "delete_notyetactive",
                    models.IntegerField(
                        default=15,
                        help_text="Not yet active users will be deleted after this number of days.",
                    ),
                ),
                (
                    "disable_emailnotyetconfirmed",
                    models.IntegerField(
                        default=2,
                        help_text="Users with an email address not yet confirmed will be disabled after this number of days.",
                    ),
                ),
                ("self_adhesion", models.BooleanField(default=False)),
                ("all_users_active", models.BooleanField(default=False)),
                (
                    "allow_set_password_during_user_creation",
                    models.BooleanField(default=False),
                ),
                ("allow_archived_connexion", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="OptionalMachine",
            bases=(re2o.mixins.AclMixin, models.Model),
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
                ("password_machine", models.BooleanField(default=False)),
                ("max_lambdauser_interfaces", models.IntegerField(default=10)),
                (
                    "ipv6_mode",
                    models.CharField(
                        choices=[
                            ("SLAAC", "Automatic configuration by RA"),
                            ("DHCPV6", "IP addresses assignment by DHCPv6"),
                            ("DISABLED", "Disabled"),
                        ],
                        default="DISABLED",
                        max_length=32,
                    ),
                ),
                ("create_machine", models.BooleanField(default=True)),
                (
                    "default_dns_ttl",
                    models.PositiveIntegerField(
                        default=172800,
                        verbose_name="default Time To Live (TTL) for CNAME, A and AAAA records",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_optionalmachine", "Can view the machine options"),
                ),
                "verbose_name": "machine options",
            },
        ),
        migrations.CreateModel(
            name="OptionalTopologie",
            bases=(re2o.mixins.AclMixin, models.Model),
            options={
                "permissions": (
                    ("view_optionaltopologie", "Can view the topology options"),
                ),
                "verbose_name": "topology options",
            },
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
                ("switchs_web_management", models.BooleanField(default=False)),
                ("switchs_web_management_ssl", models.BooleanField(default=False)),
                ("switchs_rest_management", models.BooleanField(default=False)),
                (
                    "switchs_provision",
                    models.CharField(
                        choices=[("sftp", "SFTP"), ("tftp", "TFTP")],
                        default="tftp",
                        help_text="Provision of configuration mode for switches.",
                        max_length=32,
                    ),
                ),
                (
                    "sftp_login",
                    models.CharField(
                        blank=True,
                        help_text="SFTP login for switches.",
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "sftp_pass",
                    re2o.aes_field.AESEncryptedField(
                        blank=True, help_text="SFTP password.", max_length=63, null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RadiusKey",
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
                (
                    "radius_key",
                    re2o.aes_field.AESEncryptedField(
                        help_text="Clef radius", max_length=255
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        blank=True,
                        help_text="Commentaire de cette clef",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "default_switch",
                    models.BooleanField(
                        default=True,
                        help_text="Clef par défaut des switchs",
                        unique=True,
                    ),
                ),
            ],
            options={
                "permissions": (("view_radiuskey", "Can view a RADIUS key object"),),
                "verbose_name": "RADIUS key",
                "verbose_name_plural": "RADIUS keys",
            },
            bases=(re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name="SwitchManagementCred",
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
                (
                    "management_id",
                    models.CharField(help_text="Login du switch", max_length=63),
                ),
                (
                    "management_pass",
                    re2o.aes_field.AESEncryptedField(
                        help_text="Mot de passe", max_length=63
                    ),
                ),
                (
                    "default_switch",
                    models.BooleanField(
                        default=True,
                        help_text="Creds par défaut des switchs",
                        unique=True,
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "view_switchmanagementcred",
                        "Can view a switch management credentials object",
                    ),
                ),
                "verbose_name": "switch management credentials",
            },
            bases=(re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Reminder",
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
                (
                    "days",
                    models.IntegerField(
                        default=7,
                        help_text="Délais entre le mail et la fin d'adhésion",
                        unique=True,
                    ),
                ),
                (
                    "message",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Message affiché spécifiquement pour ce rappel",
                        max_length=255,
                        null=True,
                    ),
                ),
            ],
            options={
                "permissions": (("view_reminder", "Can view a reminder object"),),
                "verbose_name": "reminder",
                "verbose_name_plural": "reminders",
            },
            bases=(re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name="GeneralOption",
            bases=(re2o.mixins.AclMixin, models.Model),
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
                (
                    "general_message_fr",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="General message displayed on the French version of the website (e.g. in case of maintenance).",
                    ),
                ),
                (
                    "general_message_en",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="General message displayed on the English version of the website (e.g. in case of maintenance).",
                    ),
                ),
                ("search_display_page", models.IntegerField(default=15)),
                ("pagination_number", models.IntegerField(default=25)),
                ("pagination_large_number", models.IntegerField(default=8)),
                ("req_expire_hrs", models.IntegerField(default=48)),
                ("site_name", models.CharField(default="Re2o", max_length=32)),
                (
                    "email_from",
                    models.EmailField(default="www-data@example.com", max_length=254),
                ),
                (
                    "main_site_url",
                    models.URLField(default="http://re2o.example.org", max_length=255),
                ),
                ("GTU_sum_up", models.TextField(blank=True, default="")),
                (
                    "GTU",
                    models.FileField(blank=True, default="", null=True, upload_to=""),
                ),
            ],
            options={
                "permissions": (
                    ("view_generaloption", "Can view the general options"),
                ),
                "verbose_name": "general options",
            },
        ),
        migrations.CreateModel(
            name="Service",
            options={
                "permissions": (("view_service", "Can view the service options"),),
                "verbose_name": "service",
                "verbose_name_plural": "services",
            },
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
                ("name", models.CharField(max_length=32)),
                ("url", models.URLField()),
                ("description", models.TextField()),
                ("image", models.ImageField(upload_to="logo")),
            ],
        ),
        migrations.CreateModel(
            name="MailContact",
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
                (
                    "address",
                    models.EmailField(
                        default="contact@example.org",
                        help_text="Contact email adress",
                        max_length=254,
                    ),
                ),
                (
                    "commentary",
                    models.CharField(
                        blank=True,
                        help_text="Description of the associated email adress.",
                        max_length=256,
                        null=True,
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_mailcontact", "Can view a contact email address object"),
                ),
                "verbose_name": "contact email address",
                "verbose_name_plural": "contact email addresses",
            },
            bases=(re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Mandate",
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
                ("start_date", models.DateTimeField(verbose_name="start date")),
                (
                    "end_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="end date"
                    ),
                ),
            ],
            options={
                "verbose_name": "Mandate",
                "verbose_name_plural": "Mandates",
                "permissions": (("view_mandate", "Can view a mandate"),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name="AssoOption",
            bases=(re2o.mixins.AclMixin, models.Model),
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
                (
                    "name",
                    models.CharField(
                        default="Networking organisation school Something",
                        max_length=256,
                    ),
                ),
                ("siret", models.CharField(default="00000000000000", max_length=32)),
                (
                    "adresse1",
                    models.CharField(default="Threadneedle Street", max_length=128),
                ),
                (
                    "adresse2",
                    models.CharField(default="London EC2R 8AH", max_length=128),
                ),
                ("contact", models.EmailField(default="contact@example.org")),
                ("telephone", models.CharField(max_length=15, default="0000000000")),
                ("pseudo", models.CharField(default="Organisation", max_length=32)),
                ("description", models.TextField(null=True, blank=True)),
            ],
            options={
                "permissions": (
                    ("view_assooption", "Can view the organisation preferences"),
                ),
                "verbose_name": "organisation preferences",
            },
        ),
        migrations.CreateModel(
            name="HomeOption",
            bases=(re2o.mixins.AclMixin, models.Model),
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
                ("facebook_url", models.URLField(null=True, blank=True)),
                ("twitter_url", models.URLField(null=True, blank=True)),
                (
                    "twitter_account_name",
                    models.CharField(max_length=32, null=True, blank=True),
                ),
            ],
            options={
                "permissions": (
                    ("view_homeoption", "Can view the homepage preferences"),
                ),
                "verbose_name": "homepage preferences",
            },
        ),
        migrations.CreateModel(
            name="MailMessageOption",
            bases=(re2o.mixins.AclMixin, models.Model),
            options={
                "permissions": (
                    (
                        "view_mailmessageoption",
                        "Can view the email message preferences",
                    ),
                ),
                "verbose_name": "email message preferences",
            },
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
                (
                    "welcome_mail_fr",
                    models.TextField(
                        default="", blank=True, help_text="Welcome email in French."
                    ),
                ),
                (
                    "welcome_mail_en",
                    models.TextField(
                        default="", blank=True, help_text="Welcome email in English."
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RadiusAttribute",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                (
                    "attribute",
                    models.CharField(
                        max_length=255,
                        verbose_name="attribute",
                        help_text="See https://freeradius.org/rfc/attributes.html.",
                    ),
                ),
                ("value", models.CharField(max_length=255, verbose_name="value")),
                (
                    "comment",
                    models.TextField(
                        verbose_name="comment",
                        help_text="Use this field to document this attribute.",
                        blank=True,
                        default="",
                    ),
                ),
            ],
            options={
                "verbose_name": "RADIUS attribute",
                "verbose_name_plural": "RADIUS attributes",
            },
        ),
        migrations.CreateModel(
            name="RadiusOption",
            bases=(re2o.mixins.AclMixin, models.Model),
            options={
                "verbose_name": "RADIUS policy",
                "verbose_name_plural": "RADIUS policies",
            },
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
                (
                    "radius_general_policy",
                    models.CharField(
                        choices=[
                            ("MACHINE", "On the IP range's VLAN of the machine"),
                            (
                                "DEFINED",
                                'Preset in "VLAN for machines accepted by RADIUS"',
                            ),
                        ],
                        default="DEFINED",
                        max_length=32,
                    ),
                ),
                (
                    "unknown_machine",
                    models.CharField(
                        choices=[
                            ("REJECT", "Reject the machine"),
                            ("SET_VLAN", "Place the machine on the VLAN"),
                        ],
                        default="REJECT",
                        max_length=32,
                        verbose_name="policy for unknown machines",
                    ),
                ),
                (
                    "unknown_port",
                    models.CharField(
                        choices=[
                            ("REJECT", "Reject the machine"),
                            ("SET_VLAN", "Place the machine on the VLAN"),
                        ],
                        default="REJECT",
                        max_length=32,
                        verbose_name="policy for unknown ports",
                    ),
                ),
                (
                    "unknown_room",
                    models.CharField(
                        choices=[
                            ("REJECT", "Reject the machine"),
                            ("SET_VLAN", "Place the machine on the VLAN"),
                        ],
                        default="REJECT",
                        max_length=32,
                        verbose_name="Policy for machines connecting from unregistered rooms (relevant on ports with STRICT RADIUS mode)",
                    ),
                ),
                (
                    "non_member",
                    models.CharField(
                        choices=[
                            ("REJECT", "Reject the machine"),
                            ("SET_VLAN", "Place the machine on the VLAN"),
                        ],
                        default="REJECT",
                        max_length=32,
                        verbose_name="policy for non members",
                    ),
                ),
                (
                    "banned",
                    models.CharField(
                        choices=[
                            ("REJECT", "Reject the machine"),
                            ("SET_VLAN", "Place the machine on the VLAN"),
                        ],
                        default="REJECT",
                        max_length=32,
                        verbose_name="policy for banned users",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CotisationsOption",
            bases=(re2o.mixins.AclMixin, models.Model),
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
                (
                    "send_voucher_mail",
                    models.BooleanField(
                        verbose_name="send voucher by email when the invoice is controlled",
                        help_text="Be careful, if no mandate is defined on the preferences page, errors will be triggered when generating vouchers.",
                        default=False,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DocumentTemplate",
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
                (
                    "template",
                    models.FileField(upload_to="templates/", verbose_name="template"),
                ),
                (
                    "name",
                    models.CharField(max_length=125, unique=True, verbose_name="name"),
                ),
            ],
            options={
                "verbose_name": "document template",
                "verbose_name_plural": "document templates",
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
    ]
