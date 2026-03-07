from django.urls import path
from .views import VideoListView, VideoMasterPlaylistView, VideoSegmentView, DeleteVideoMasterPlaylistView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8/', VideoMasterPlaylistView.as_view(), name='video_master_playlist'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),
    path('video/<int:movie_id>/', DeleteVideoMasterPlaylistView.as_view(), name='delete_video_master_playlist'),
]