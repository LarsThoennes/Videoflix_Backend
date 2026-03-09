import os
import shutil
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.utils.text import slugify
from ..models import Video
from .serializers import VideoSerializer
from ..permissions import IsStaff

class VideoListView(APIView):
    """
    API endpoint to list all videos.

    This view handles:
    - retrieving all Video instances from the database
    - serializing the videos for API response
    - returning a JSON list of videos with HTTP 200 OK
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all()

        serializer = VideoSerializer(
            videos,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoMasterPlaylistView(APIView):
    """
    API endpoint to retrieve a master playlist (.m3u8) for a specific video.

    This view handles:
    - validating the video exists by ID
    - checking that the requested resolution is valid (480p, 720p, 1080p)
    - reading the HLS master playlist file from the filesystem
    - returning the playlist content with the correct MIME type
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")
        
        if resolution not in ["480p", "720p", "1080p"]:
            raise Http404("Invalid resolution")
        
        slugify_title = slugify(video.title)

        manifest_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            "processed",
            str(video.id),
            resolution,
            f"{slugify_title}.m3u8"
        )

        if not os.path.exists(manifest_path):
            raise Http404("Manifest not found")

        with open(manifest_path, "r") as f:
            manifest_content = f.read()

        return HttpResponse(
            manifest_content,
            content_type="application/vnd.apple.mpegurl"
        )
    
class VideoSegmentView(APIView):
    """
    API endpoint to retrieve individual HLS video segments (.ts).

    This view handles:
    - validating the video exists by ID
    - checking that the requested resolution and segment filename are valid
    - reading the segment file from the filesystem
    - returning the segment as a video/MP2T file response
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")
        
        if resolution not in ["480p", "720p", "1080p"]:
            raise Http404("Invalid resolution")
        
        if not segment.endswith(".ts"):
            raise Http404("Invalid segment")
        
        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            "processed",
            str(video.id),
            resolution,
            segment
        )

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")
        
        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T"
        )
    
class DeleteVideoMasterPlaylistView(APIView):
    """
    API endpoint to delete a video and all associated files.

    This view handles:
    - validating that the user has staff permissions
    - locating all processed, thumbnail, and original video files
    - removing all related files and directories from the filesystem
    - deleting the Video instance from the database
    - returning HTTP 204 No Content on success
    """
    permission_classes = [IsStaff]

    def delete(self, request, movie_id):
        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")
        

        processed_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            "processed",
            str(video.id)
        )

        thumbnail_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            "thumbnails",
            str(video.id)
        )

        original_file_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            "originals",
            str(video.id)
        )

        if os.path.exists(original_file_path):
            shutil.rmtree(original_file_path)

        if os.path.exists(thumbnail_path):
            shutil.rmtree(thumbnail_path)

        if os.path.exists(processed_path):
            shutil.rmtree(processed_path)

        video.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)