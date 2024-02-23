# models.py
from django.db import models,transaction
from missions.models import Mission
class File(models.Model):
    name = models.CharField(max_length=255)
    picture = models.FileField(upload_to='uploads/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    mission = models.ForeignKey(Mission, verbose_name=("mission"), on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'uploadedPictures'

class Video(models.Model):
    name = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='uploads/videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    mission = models.ForeignKey(Mission, verbose_name=("mission"), on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'uploadedVideos'
        

class RealTime(models.Model):
    aircraft_lat = models.FloatField()
    aircraft_lon = models.FloatField()
    target_lat = models.FloatField()
    target_lon = models.FloatField()  # Corrected field name
    file = models.ForeignKey(File, verbose_name=("file"), on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    is_latest = models.BooleanField()

    
    class Meta:
        db_table = 'live'