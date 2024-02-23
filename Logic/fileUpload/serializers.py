# serializers.py
from rest_framework import serializers
from .models import File, Video , RealTime

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class RealTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTime
        fields = '__all__'
