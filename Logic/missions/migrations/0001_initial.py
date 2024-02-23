# Generated by Django 4.2.6 on 2023-11-28 15:39

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'db_table': 'location',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('drone', models.CharField(max_length=255)),
                ('discription', models.TextField(blank=True, null=True)),
                ('started', models.DateTimeField()),
                ('area', django.contrib.gis.db.models.fields.PolygonField(blank=True, db_column='Area', null=True, srid=4326)),
                ('id_flight', models.CharField(blank=True, max_length=50, null=True)),
                ('uuid', models.CharField(blank=True, max_length=50, null=True)),
                ('published', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'mission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('path_img', models.CharField(blank=True, max_length=128, null=True)),
                ('northern', models.CharField(blank=True, db_column='Northern', max_length=20, null=True)),
                ('eastern', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'picture',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WorldBorder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('area', models.IntegerField()),
                ('pop2005', models.IntegerField(verbose_name='Population 2005')),
                ('fips', models.CharField(max_length=2, null=True, verbose_name='FIPS Code')),
                ('iso2', models.CharField(max_length=2, verbose_name='2 Digit ISO')),
                ('iso3', models.CharField(max_length=3, verbose_name='3 Digit ISO')),
                ('un', models.IntegerField(verbose_name='United Nations Code')),
                ('region', models.IntegerField(verbose_name='Region Code')),
                ('subregion', models.IntegerField(verbose_name='Sub-Region Code')),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'db_table': 'world_borders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Delegations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_del', models.CharField(max_length=255)),
                ('del_fr', models.CharField(max_length=255)),
                ('del_ar', models.CharField(max_length=255)),
                ('gouv_id', models.CharField(max_length=255)),
                ('gouv_fr', models.CharField(max_length=255)),
                ('gouv_ar', models.CharField(max_length=255)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'db_table': 'delegations',
                'managed': True,
            },
        ),
    ]