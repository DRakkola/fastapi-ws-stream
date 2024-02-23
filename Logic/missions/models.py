from uuid import uuid4
from django.db import models

# Create your models here.
from django.contrib.gis.db import models as gis_models
from django.db.models import DateTimeField
from django.contrib.gis.geos import Point
class DateTimeWithoutTZField(DateTimeField):
    def db_type(self, connection):
        return 'timestamp without time zone'
    
    
class WorldBorder(gis_models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = gis_models.CharField(max_length=50)
    area = gis_models.IntegerField()
    pop2005 = gis_models.IntegerField("Population 2005")
    fips = gis_models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = gis_models.CharField("2 Digit ISO", max_length=2)
    iso3 = gis_models.CharField("3 Digit ISO", max_length=3)
    un = gis_models.IntegerField("United Nations Code")
    region = gis_models.IntegerField("Region Code")
    subregion = gis_models.IntegerField("Sub-Region Code")
    lon = gis_models.FloatField()
    lat = gis_models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = gis_models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name
    class Meta:
        db_table = "world_borders"
        managed = False

class Location(models.Model):
    id = models.UUIDField(primary_key=True)
    timestamp = models.DateTimeField()
    lon = models.FloatField()
    lat = models.FloatField()
    geometry = gis_models.PointField()
    mission = models.ForeignKey('Mission', related_name='locations', on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'location'
    def save(self, *args, **kwargs):
        # Automatically generate geometry field from lat and lon
        if self.lat is not None and self.lon is not None:
            self.geometry = Point(self.lon, self.lat)
        super().save(*args, **kwargs)


class Mission(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    drone = models.CharField(max_length=255)
    discription = models.TextField(blank=True, null=True)
    started = models.DateTimeField()
    area = gis_models.PolygonField(db_column='Area', blank=True, null=True)  # Field name made lowercase.
    id_flight = models.CharField(max_length=50, blank=True, null=True)
    uuid = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField(blank=True, null=True)
    live = models.BooleanField(blank=True, null=True)
    def __str__(self):
        return self.name
    class Meta:
        managed = False
        db_table = 'mission'


class Delegations(models.Model):
    id_del = gis_models.CharField(max_length=255)
    del_fr = gis_models.CharField(max_length=255)
    del_ar = gis_models.CharField(max_length=255)
    gouv_id = gis_models.CharField(max_length=255)
    gouv_fr = gis_models.CharField(max_length=255)
    gouv_ar = gis_models.CharField(max_length=255)
    geometry = gis_models.MultiPolygonField()


    class Meta:
        managed = True
        db_table = 'delegations'


class Picture(models.Model):
    id = models.UUIDField(primary_key=True)
    timestamp = models.DateTimeField()
    geometry = gis_models.PointField()
    lon = models.FloatField()
    lat = models.FloatField()
    mission = models.ForeignKey('Mission', related_name='pictures', on_delete=models.DO_NOTHING)
    path_img = models.CharField(max_length=128, blank=True, null=True)
    northern = models.CharField(db_column='Northern', max_length=20, blank=True, null=True)  # Field name made lowercase.
    eastern = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'picture'
    def save(self, *args, **kwargs):
        # Automatically generate geometry field from lat and lon
        if self.lat is not None and self.lon is not None:
            self.geometry = Point(self.lon, self.lat)
        super().save(*args, **kwargs)
