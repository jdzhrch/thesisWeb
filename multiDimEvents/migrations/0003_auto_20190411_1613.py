# Generated by Django 2.2 on 2019-04-11 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multiDimEvents', '0002_event_searchnum'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-searchNum']},
        ),
    ]
