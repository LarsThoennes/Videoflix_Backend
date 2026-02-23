import os
import django_rq
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
from .tasks import convert_video_to_480p

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print("Video post save signal triggered")
    if created:
        print(f"New video created")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_video_to_480p, instance.video_file.path)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    print("Video post delete signal triggered")
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print(f"Deleted video file: {instance.video_file.path}")