from django.urls import path
from .views import VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video'),
    # path('video/<int:movie_id>/<str:resolution>/index.m3u8/', VideoIndexView.as_view(), name='video_index'),
    # path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),
]