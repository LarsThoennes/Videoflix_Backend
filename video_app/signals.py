import django_rq
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Video
from .tasks import convert_video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if not instance.original_file:
        return
    queue = django_rq.get_queue('default')
    queue.enqueue(convert_video, instance.id)