# Generated by Django 2.2.18 on 2021-02-14 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_squashed_0007'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commentticket',
            options={'verbose_name': 'ticket', 'verbose_name_plural': 'tickets'},
        ),
        migrations.AlterModelOptions(
            name='ticket',
            options={'verbose_name': 'ticket', 'verbose_name_plural': 'tickets'},
        ),
        migrations.AlterModelOptions(
            name='ticketoption',
            options={'verbose_name': 'tickets options'},
        ),
    ]