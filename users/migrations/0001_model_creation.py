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
    dependencies = [('auth', '0008_alter_user_username_max_length')]
    initial = True
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
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128, verbose_name="password"
                    ),
                ),
                ("groups", models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ("user_permissions", models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'))
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
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128, verbose_name="password"
                    ),
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
                    "group_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        on_delete=django.db.models.deletion.CASCADE,
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
