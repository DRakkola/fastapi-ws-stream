# views.py
from rest_framework import viewsets
from .models import File, Video,RealTime
from .serializers import FileSerializer, VideoSerializer,RealTimeSerializer

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class RealTimeViewSet(viewsets.ModelViewSet):
    queryset = RealTime.objects.all()
    serializer_class = RealTimeSerializer
