from django.db import models
from django.utils import timezone


class Video(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=100)

    original_file = models.FileField(upload_to='videos/originals/', null=True, blank=True)

    def __str__(self):
        return self.title


class VideoFile(models.Model):
    RESOLUTION_CHOICES = [
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    ]

    video = models.ForeignKey(
        Video,
        related_name='files',
        on_delete=models.CASCADE
    )
    resolution = models.CharField(max_length=10, choices=RESOLUTION_CHOICES)
    file = models.FileField(upload_to='videos/processed/')

    def __str__(self):
        return f"{self.video.title} - {self.resolution}"