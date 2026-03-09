from rest_framework import serializers
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video model instances.

    This serializer handles:
    - converting Video model fields to JSON for API responses
    - including key information such as ID, title, description, thumbnail, and category
    - exposing the creation timestamp of the video
    """

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]