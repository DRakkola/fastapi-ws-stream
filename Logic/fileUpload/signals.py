import os
from django.db import models
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from queue import Queue
import threading
from .utils import save_valuable

# Assuming Mission model is defined elsewhere
from .models import File, RealTime
from missions.models import Mission
from datetime import datetime

# Create a queue to manage the processing order
file_processing_queue = Queue()


# Define a function to process files
def process_file(file_instance):
    try:
        aircraft, target, name = save_valuable(file_instance.picture.path)
        if aircraft and target and name :
            real_time_data = RealTime(
                aircraft_lat=aircraft[0],
                aircraft_lon=aircraft[1],
                target_lat=target[0],
                target_lon=target[1],
                file=file_instance,  # Assuming you have a Mission instance available
                date=datetime.now().date(),  # Set the date to the current date
                time=datetime.now().time(),
                is_latest = True
            )
            real_time_data.save()
            file_instance.processed = True
    except Exception as e:
        # Log the exception or handle it as required
        # In this example, we're printing the exception
        print(f"File processing failed: {e}")
        # Delete the file
        file_path = file_instance.picture.path
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the row
        file_instance.delete()
    else:
        file_instance.save()


# Define a function to consume files from the queue and process them
def process_queue():
    while True:
        file_instance = file_processing_queue.get()
        process_file(file_instance)
        file_processing_queue.task_done()


# Start a thread to continuously process the queue
processing_thread = threading.Thread(target=process_queue)
processing_thread.daemon = True
processing_thread.start()


# Signal receiver to add files to the processing queue when they are created
@receiver(post_save, sender=File)
def queue_file_processing(sender, instance, created, **kwargs):
    if created:
        file_processing_queue.put(instance)

@receiver(pre_save, sender=RealTime)
def highlightCurrentPosition(sender,*args,**kwargs):
    sender.objects.update(is_latest=False)