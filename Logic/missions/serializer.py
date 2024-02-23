from rest_framework import serializers
from django.contrib.gis.db import models as gis_models
from .models import WorldBorder, Location, Mission,Picture,Delegations


class WorldBorderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorldBorder
        fields = '__all__'



class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['id', 'name', 'drone', 'started', 'area', 'id_flight', 'uuid', 'published']

class LocationSerializer(serializers.ModelSerializer):
    mission = MissionSerializer()
    class Meta:
        model = Location
        fields = ['id', 'timestamp', 'lon', 'lat', 'geometry', 'mission']
        
class PictureSerializer(serializers.ModelSerializer):
    mission = MissionSerializer()
    class Meta:
        model = Picture
        fields = '__all__'

class MissionDetailSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    pictures = PictureSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ['id', 'name', 'drone', 'discription', 'started', 'id_flight', 'published', 'locations', 'pictures']

class DelegationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delegations
        fields = '__all__'
        
        


class DistanceSerializer(serializers.Serializer):
    total_distance_month = serializers.FloatField()
    daily_distances = serializers.DictField(child=serializers.FloatField())

class PictureCountSerializer(serializers.Serializer):
    year = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    total = serializers.IntegerField()

    def get_year(self, obj):
        return obj['month'].year

    def get_name(self, obj):
        return obj['month'].strftime('%b')