import django_rq
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Video
from .tasks import convert_video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler triggered after a Video instance is saved.

    This signal handles:
    - checking if an original video file exists
    - enqueueing a background task for video conversion
    - processing the video asynchronously using django-rq
    """
    if not instance.original_file:
        return
    queue = django_rq.get_queue('default')
    queue.enqueue(convert_video, instance.id)