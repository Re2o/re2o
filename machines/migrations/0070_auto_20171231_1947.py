# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-31 18:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("machines", "0069_auto_20171116_0822")]

    operations = [
        migrations.AlterModelOptions(
            name="domain",
            options={"permissions": (("view_domain", "Peut voir un objet domain"),)},
        ),
        migrations.AlterModelOptions(
            name="extension",
            options={
                "permissions": (
                    ("view_extension", "Peut voir un objet extension"),
                    ("use_all_extension", "Peut utiliser toutes les extension"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="interface",
            options={
                "permissions": (("view_interface", "Peut voir un objet interface"),)
            },
        ),
        migrations.AlterModelOptions(
            name="iplist",
            options={"permissions": (("view_iplist", "Peut voir un objet iplist"),)},
        ),
        migrations.AlterModelOptions(
            name="iptype",
            options={
                "permissions": (
                    ("view_iptype", "Peut voir un objet iptype"),
                    ("use_all_iptype", "Peut utiliser tous les iptype"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="machine",
            options={
                "permissions": (
                    ("view_machine", "Peut voir un objet machine quelquonque"),
                    (
                        "change_machine_user",
                        "Peut changer le propriétaire d'une machine",
                    ),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="machinetype",
            options={
                "permissions": (
                    ("view_machinetype", "Peut voir un objet machinetype"),
                    (
                        "use_all_machinetype",
                        "Peut utiliser n'importe quel type de machine",
                    ),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="mx", options={"permissions": (("view_mx", "Peut voir un objet mx"),)}
        ),
        migrations.AlterModelOptions(
            name="nas",
            options={"permissions": (("view_nas", "Peut voir un objet Nas"),)},
        ),
        migrations.AlterModelOptions(
            name="ns", options={"permissions": (("view_nx", "Peut voir un objet nx"),)}
        ),
        migrations.AlterModelOptions(
            name="ouvertureportlist",
            options={
                "permissions": (
                    ("view_ouvertureportlist", "Peut voir un objet ouvertureport"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="service",
            options={"permissions": (("view_service", "Peut voir un objet service"),)},
        ),
        migrations.AlterModelOptions(
            name="soa",
            options={"permissions": (("view_soa", "Peut voir un objet soa"),)},
        ),
        migrations.AlterModelOptions(
            name="srv",
            options={"permissions": (("view_soa", "Peut voir un objet soa"),)},
        ),
        migrations.AlterModelOptions(
            name="txt",
            options={"permissions": (("view_txt", "Peut voir un objet txt"),)},
        ),
        migrations.AlterModelOptions(
            name="vlan",
            options={"permissions": (("view_vlan", "Peut voir un objet vlan"),)},
        ),
    ]
