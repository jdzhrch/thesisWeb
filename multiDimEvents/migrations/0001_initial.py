# Generated by Django 2.2 on 2019-04-10 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eventName', models.CharField(max_length=200)),
                ('reportTime', models.DateField(auto_now_add=True, verbose_name='time when report is generated')),
                ('reportVer', models.IntegerField(default=1)),
                ('categoryNum', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(default='000', max_length=200)),
                ('eventId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiDimEvents.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featureList', models.CharField(max_length=200)),
                ('reportVer', models.IntegerField(default=1)),
                ('articleNum', models.IntegerField(default=0)),
                ('eventId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiDimEvents.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=400)),
                ('content', models.TextField(max_length=40000)),
                ('pv', models.IntegerField(default=0)),
                ('categoryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multiDimEvents.Event')),
            ],
        ),
    ]
