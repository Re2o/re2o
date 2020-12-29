# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
import re2o.mixins
import re2o.field_permissions
import users.models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    replaces = [
        ("users", "0001_initial.py"),
        ("users", "0002_auto_20160630_2301.py"),
        ("users", "0003_listrights_rights.py"),
        ("users", "0004_auto_20160701_2312.py"),
        ("users", "0005_auto_20160702_0006.py"),
        ("users", "0006_ban.py"),
        ("users", "0007_auto_20160702_2322.py"),
        ("users", "0008_user_registered.py"),
        ("users", "0009_user_room.py"),
        ("users", "0010_auto_20160703_1226.py"),
        ("users", "0011_auto_20160703_1227.py"),
        ("users", "0012_auto_20160703_1230.py"),
        ("users", "0013_auto_20160704_1547.py"),
        ("users", "0014_auto_20160704_1548.py"),
        ("users", "0015_whitelist.py"),
        ("users", "0016_auto_20160706_1220.py"),
        ("users", "0017_auto_20160707_0105.py"),
        ("users", "0018_auto_20160707_0115.py"),
        ("users", "0019_auto_20160708_1633.py"),
        ("users", "0020_request.py"),
        ("users", "0021_ldapuser.py"),
        ("users", "0022_ldapuser_sambasid.py"),
        ("users", "0023_auto_20160724_1908.py"),
        ("users", "0024_remove_ldapuser_mac_list.py"),
        ("users", "0025_listshell.py"),
        ("users", "0026_user_shell.py"),
        ("users", "0027_auto_20160726_0216.py"),
        ("users", "0028_auto_20160726_0227.py"),
        ("users", "0029_auto_20160726_0229.py"),
        ("users", "0030_auto_20160726_0357.py"),
        ("users", "0031_auto_20160726_0359.py"),
        ("users", "0032_auto_20160727_2122.py"),
        ("users", "0033_remove_ldapuser_loginshell.py"),
        ("users", "0034_auto_20161018_0037.py"),
        ("users", "0035_auto_20161018_0046.py"),
        ("users", "0036_auto_20161022_2146.py"),
        ("users", "0037_auto_20161028_1906.py"),
        ("users", "0038_auto_20161031_0258.py"),
        ("users", "0039_auto_20161119_0033.py"),
        ("users", "0040_auto_20161119_1709.py"),
        ("users", "0041_listright_details.py"),
        ("users", "0042_auto_20161126_2028.py"),
        ("users", "0043_auto_20161224_1156.py"),
        ("users", "0043_ban_state.py"),
        ("users", "0044_user_ssh_public_key.py"),
        ("users", "0045_merge.py"),
        ("users", "0046_auto_20170617_1433.py"),
        ("users", "0047_auto_20170618_0156.py"),
        ("users", "0048_auto_20170618_0210.py"),
        ("users", "0049_auto_20170618_1424.py"),
        ("users", "0050_serviceuser_comment.py"),
        ("users", "0051_user_telephone.py"),
        ("users", "0052_ldapuser_shadowexpire.py"),
        ("users", "0053_auto_20170626_2105.py"),
        ("users", "0054_auto_20170626_2219.py"),
        ("users", "0055_auto_20171003_0556.py"),
        ("users", "0056_auto_20171015_2033.py"),
        ("users", "0057_auto_20171023_0301.py"),
        ("users", "0058_auto_20171025_0154.py"),
        ("users", "0059_auto_20171025_1854.py"),
        ("users", "0060_auto_20171120_0317.py"),
        ("users", "0061_auto_20171230_2033.py"),
        ("users", "0062_auto_20171231_0056.py"),
        ("users", "0063_auto_20171231_0140.py"),
        ("users", "0064_auto_20171231_0150.py"),
        ("users", "0065_auto_20171231_2053.py"),
        ("users", "0066_grouppermissions.py"),
        ("users", "0067_serveurpermission.py"),
        ("users", "0068_auto_20180107_2245.py"),
        ("users", "0069_club_mailing.py"),
        ("users", "0070_auto_20180324_1906.py"),
        ("users", "0071_auto_20180415_1252.py"),
        ("users", "0072_auto_20180426_2021.py"),
        ("users", "0073_auto_20180629_1614.py"),
        ("users", "0074_auto_20180810_2104.py"),
        ("users", "0074_auto_20180814_1059.py"),
        ("users", "0075_merge_20180815_2202.py"),
        ("users", "0076_auto_20180818_1321.py"),
        ("users", "0077_auto_20180824_1750.py"),
        ("users", "0078_auto_20181011_1405.py"),
        ("users", "0079_auto_20181228_2039.py"),
        ("users", "0080_auto_20190108_1726.py"),
        ("users", "0081_auto_20190317_0302.py"),
        ("users", "0082_auto_20190908_1338.py"),
        ("users", "0083_user_shortcuts_enabled.py"),
        ("users", "0084_auto_20191120_0159.py"),
        ("users", "0085_user_email_state.py"),
        ("users", "0086_user_email_change_date.py"),
        ("users", "0087_request_email.py"),
        ("users", "0088_auto_20200417_2312.py"),
        ("users", "0089_auto_20200418_0112.py"),
        ("users", "0090_auto_20200421_1825.py"),
        ("users", "0091_auto_20200423_1256.py"),
        ("users", "0092_auto_20200502_0057.py"),
        ("users", "0093_user_profile_image.py"),
        ("users", "0094_remove_user_profile_image.py"),
        ("users", "0095_user_theme.py"),
    ]
    operations = [
        migrations.CreateModel(
            name="User",
            bases=(
                re2o.mixins.RevMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
                django.contrib.auth.models.AbstractBaseUser,
                django.contrib.auth.models.PermissionsMixin,
                re2o.mixins.AclMixin,
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
                ("surname", models.CharField(max_length=255)),
                (
                    "pseudo",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        help_text="Must only contain letters, numerals or dashes.",
                        validators=[users.models.linux_user_validator],
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        default="",
                        help_text="External email address allowing us to contact you.",
                    ),
                ),
                (
                    "local_email_redirect",
                    models.BooleanField(
                        default=False,
                        help_text="Enable redirection of the local email messages to the main email address.",
                    ),
                ),
                (
                    "local_email_enabled",
                    models.BooleanField(
                        default=False, help_text="Enable the local email account."
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        help_text="Comment, school year.", max_length=255, blank=True
                    ),
                ),
                ("pwd_ntlm", models.CharField(max_length=255)),
                (
                    "state",
                    models.IntegerField(
                        choices=(
                            (0, "Active"),
                            (1, "Disabled"),
                            (2, "Archived"),
                            (3, "Not yet active"),
                            (4, "Fully archived"),
                        ),
                        default=3,
                        help_text="Account state.",
                    ),
                ),
                (
                    "email_state",
                    models.IntegerField(
                        choices=(
                            (0, "Confirmed"),
                            (1, "Not confirmed"),
                            (2, "Waiting for email confirmation"),
                        ),
                        default=2,
                    ),
                ),
                ("registered", models.DateTimeField(auto_now_add=True)),
                ("telephone", models.CharField(max_length=15, blank=True, null=True)),
                (
                    "uid_number",
                    models.PositiveIntegerField(
                        default=users.models.get_fresh_user_uid, unique=True
                    ),
                ),
                (
                    "legacy_uid",
                    models.PositiveIntegerField(
                        unique=True,
                        blank=True,
                        null=True,
                        help_text="Optionnal legacy uid, for import and transition purpose",
                    ),
                ),
                (
                    "shortcuts_enabled",
                    models.BooleanField(
                        verbose_name="enable shortcuts on Re2o website", default=True
                    ),
                ),
                ("email_change_date", models.DateTimeField(auto_now_add=True)),
                ("theme", models.CharField(max_length=255, default="default.css")),
            ],
            options={
                "permissions": (
                    ("change_user_password", "Can change the password of a user"),
                    ("change_user_state", "Can edit the state of a user"),
                    ("change_user_force", "Can force the move"),
                    ("change_user_shell", "Can edit the shell of a user"),
                    ("change_user_pseudo", "Can edit the pseudo of a user"),
                    (
                        "change_user_groups",
                        "Can edit the groups of rights of a user (critical permission)",
                    ),
                    (
                        "change_all_users",
                        "Can edit all users, including those with rights",
                    ),
                    ("view_user", "Can view a user object"),
                ),
                "verbose_name": "user (member or club)",
                "verbose_name_plural": "users (members or clubs)",
            },
        ),
        migrations.CreateModel(
            name="Adherent",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "gpg_fingerprint",
                    models.CharField(max_length=49, blank=True, null=True),
                ),
            ],
            options={"verbose_name": "member", "verbose_name_plural": "members"},
        ),
        migrations.CreateModel(
            name="Club",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("mailing", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "club", "verbose_name_plural": "clubs"},
        ),
        migrations.CreateModel(
            name="ServiceUser",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                django.contrib.auth.models.AbstractBaseUser,
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
                    "pseudo",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        help_text="Must only contain letters, numerals or dashes.",
                        validators=[users.models.linux_user_validator],
                    ),
                ),
                (
                    "access_group",
                    models.CharField(
                        choices=(
                            ("auth", "auth"),
                            ("readonly", "readonly"),
                            ("usermgmt", "usermgmt"),
                        ),
                        default="readonly",
                        max_length=32,
                    ),
                ),
                (
                    "comment",
                    models.CharField(help_text="Comment.", max_length=255, blank=True),
                ),
            ],
            options={
                "permissions": (
                    ("view_serviceuser", "Can view a service user object"),
                ),
                "verbose_name": "service user",
                "verbose_name_plural": "service users",
            },
        ),
        migrations.CreateModel(
            name="School",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                "permissions": (("view_school", "Can view a school object"),),
                "verbose_name": "school",
                "verbose_name_plural": "schools",
            },
        ),
        migrations.CreateModel(
            name="ListRight",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                django.contrib.auth.models.Group,
            ),
            fields=[
                (
                    "id",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="auth.Group",
                    ),
                ),
                (
                    "unix_name",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[a-z]+$",
                                message=(
                                    "UNIX group names can only contain lower case letters."
                                ),
                            )
                        ],
                    ),
                ),
                ("gid", models.PositiveIntegerField(unique=True, null=True)),
                ("critical", models.BooleanField(default=False)),
                (
                    "details",
                    models.CharField(
                        help_text="Description.", max_length=255, blank=True
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_listright", "Can view a group of rights object"),
                ),
                "verbose_name": "group of rights",
                "verbose_name_plural": "groups of rights",
            },
        ),
        migrations.CreateModel(
            name="ListShell",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                ("shell", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "permissions": (("view_listshell", "Can view a shell object"),),
                "verbose_name": "shell",
                "verbose_name_plural": "shells",
            },
        ),
        migrations.CreateModel(
            name="Ban",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                ("raison", models.CharField(max_length=255)),
                ("date_start", models.DateTimeField(auto_now_add=True)),
                ("date_end", models.DateTimeField()),
                (
                    "state",
                    models.IntegerField(
                        choices=(
                            (0, "HARD (no access)"),
                            (1, "SOFT (local access only)"),
                            (2, "RESTRICTED (speed limitation)"),
                        ),
                        default=0,
                    ),
                ),
            ],
            options={
                "permissions": (("view_ban", "Can view a ban object"),),
                "verbose_name": "ban",
                "verbose_name_plural": "bans",
            },
        ),
        migrations.CreateModel(
            name="Whitelist",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                ("raison", models.CharField(max_length=255)),
                ("date_start", models.DateTimeField(auto_now_add=True)),
                ("date_end", models.DateTimeField()),
            ],
            options={
                "permissions": (("view_whitelist", "Can view a whitelist object"),),
                "verbose_name": "whitelist (free of charge access)",
                "verbose_name_plural": "whitelists (free of charge access)",
            },
        ),
        migrations.CreateModel(
            name="Request",
            bases=(models.Model,),
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
                    "type",
                    models.CharField(
                        max_length=2,
                        choices=(("PW", "Password"), ("EM", "Email address")),
                    ),
                ),
                ("token", models.CharField(max_length=32)),
                ("email", models.EmailField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
                ("expires_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="EMailAddress",
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
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
                    "local_part",
                    models.CharField(
                        unique=True,
                        max_length=128,
                        help_text="Local part of the email address.",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_emailaddress", "Can view a local email account object"),
                ),
                "verbose_name": "local email account",
                "verbose_name_plural": "local email accounts",
            },
        ),
    ]
