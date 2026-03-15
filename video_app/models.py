from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def thumbnail_upload_path(instance, filename):
    return f'videos/thumbnails/{instance.id}/{filename}'


def video_upload_path(instance, filename):
    return f'videos/originals/{instance.id}/{filename}'


class Video(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)

    thumbnail_url = models.ImageField(
        upload_to=thumbnail_upload_path,
        null=True,
        blank=True
    )

    original_file = models.FileField(
        upload_to=video_upload_path,
        null=True,
        blank=True
    )

    def clean(self):
        if not self.thumbnail_url:
            raise ValidationError({"thumbnail_url": "Thumbnail is required."})

        if not self.original_file:
            raise ValidationError({"original_file": "Original video file is required."})

    def save(self, *args, **kwargs):
        if self.pk is None:
            thumbnail = self.thumbnail_url
            video = self.original_file

            self.thumbnail_url = None
            self.original_file = None

            super().save(*args, **kwargs)

            self.thumbnail_url = thumbnail
            self.original_file = video

        super().save(*args, **kwargs)

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