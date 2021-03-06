# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-08-18 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0049_optionaluser_self_change_shell")]

    operations = [
        migrations.AlterModelOptions(
            name="assooption",
            options={
                "permissions": (
                    ("view_assooption", "Can view the organisation options"),
                ),
                "verbose_name": "organisation options",
            },
        ),
        migrations.AlterModelOptions(
            name="generaloption",
            options={
                "permissions": (
                    ("view_generaloption", "Can view the general options"),
                ),
                "verbose_name": "general options",
            },
        ),
        migrations.AlterModelOptions(
            name="homeoption",
            options={
                "permissions": (("view_homeoption", "Can view the homepage options"),),
                "verbose_name": "homepage options",
            },
        ),
        migrations.AlterModelOptions(
            name="mailcontact",
            options={
                "permissions": (
                    ("view_mailcontact", "Can view a contact email address object"),
                ),
                "verbose_name": "contact email address",
                "verbose_name_plural": "contact email addresses",
            },
        ),
        migrations.AlterModelOptions(
            name="mailmessageoption",
            options={
                "permissions": (
                    ("view_mailmessageoption", "Can view the email message options"),
                ),
                "verbose_name": "email message options",
            },
        ),
        migrations.AlterModelOptions(
            name="optionalmachine",
            options={
                "permissions": (
                    ("view_optionalmachine", "Can view the machine options"),
                ),
                "verbose_name": "machine options",
            },
        ),
        migrations.AlterModelOptions(
            name="optionaltopologie",
            options={
                "permissions": (
                    ("view_optionaltopologie", "Can view the topology options"),
                ),
                "verbose_name": "topology options",
            },
        ),
        migrations.AlterModelOptions(
            name="optionaluser",
            options={
                "permissions": (("view_optionaluser", "Can view the user options"),),
                "verbose_name": "user options",
            },
        ),
        migrations.AlterModelOptions(
            name="service",
            options={
                "permissions": (("view_service", "Can view the service options"),),
                "verbose_name": "service",
                "verbose_name_plural": "services",
            },
        ),
        migrations.AlterField(
            model_name="assooption",
            name="adresse1",
            field=models.CharField(default="Threadneedle Street", max_length=128),
        ),
        migrations.AlterField(
            model_name="assooption",
            name="adresse2",
            field=models.CharField(default="London EC2R 8AH", max_length=128),
        ),
        migrations.AlterField(
            model_name="assooption",
            name="name",
            field=models.CharField(
                default="Networking organisation school Something", max_length=256
            ),
        ),
        migrations.AlterField(
            model_name="assooption",
            name="pseudo",
            field=models.CharField(default="Organisation", max_length=32),
        ),
        migrations.AlterField(
            model_name="generaloption",
            name="general_message_en",
            field=models.TextField(
                blank=True,
                default="",
                help_text="General message displayed on the English version of the website (e.g. in case of maintenance)",
            ),
        ),
        migrations.AlterField(
            model_name="generaloption",
            name="general_message_fr",
            field=models.TextField(
                blank=True,
                default="",
                help_text="General message displayed on the French version of the website (e.g. in case of maintenance)",
            ),
        ),
        migrations.AlterField(
            model_name="homeoption",
            name="facebook_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="homeoption",
            name="twitter_account_name",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name="homeoption",
            name="twitter_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="mailcontact",
            name="address",
            field=models.EmailField(
                default="contact@example.org",
                help_text="Contact email address",
                max_length=254,
            ),
        ),
        migrations.AlterField(
            model_name="mailcontact",
            name="commentary",
            field=models.CharField(
                blank=True,
                help_text="Description of the associated email address.",
                max_length=256,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="optionalmachine",
            name="create_machine",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="optionalmachine",
            name="ipv6_mode",
            field=models.CharField(
                choices=[
                    ("SLAAC", "Autoconfiguration by RA"),
                    ("DHCPV6", "IP addresses assigning by DHCPv6"),
                    ("DISABLED", "Disabled"),
                ],
                default="DISABLED",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="optionaltopologie",
            name="radius_general_policy",
            field=models.CharField(
                choices=[
                    ("MACHINE", "On the IP range's VLAN of the machine"),
                    ("DEFINED", "Preset in 'VLAN for machines accepted by RADIUS'"),
                ],
                default="DEFINED",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="optionaluser",
            name="all_can_create_adherent",
            field=models.BooleanField(
                default=False, help_text="Users can create a member"
            ),
        ),
        migrations.AlterField(
            model_name="optionaluser",
            name="all_can_create_club",
            field=models.BooleanField(
                default=False, help_text="Users can create a club"
            ),
        ),
        migrations.AlterField(
            model_name="optionaluser",
            name="max_email_address",
            field=models.IntegerField(
                default=15,
                help_text="Maximum number of local email addresses for a standard user",
            ),
        ),
        migrations.AlterField(
            model_name="optionaluser",
            name="self_adhesion",
            field=models.BooleanField(
                default=False, help_text="A new user can create their account on Re2o"
            ),
        ),
        migrations.AlterField(
            model_name="optionaluser",
            name="self_change_shell",
            field=models.BooleanField(
                default=False, help_text="Users can edit their shell"
            ),
        ),
    ]
