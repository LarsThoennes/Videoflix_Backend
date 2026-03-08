import subprocess
import os
from django.conf import settings
from django.utils.text import slugify
from video_app.models import Video, VideoFile


def convert_video(video_id):
    video = Video.objects.get(id=video_id)
    source = video.original_file.path

    safe_title = slugify(video.title)

    output_base = os.path.join(
        settings.MEDIA_ROOT,
        "videos",
        "processed",
        str(video.id)
    )

    resolutions = {
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
    }

    for label, height in resolutions.items():
        resolution_dir = os.path.join(output_base, label)
        os.makedirs(resolution_dir, exist_ok=True)
    
        playlist_name = f"{safe_title}.m3u8"
        output_path = os.path.join(resolution_dir, playlist_name)

        segment_pattern = os.path.join(
            resolution_dir,
            "%04d.ts" 
        )
    
        cmd = [
            "ffmpeg",
            "-y",
            "-i", source,
            "-c:v", "libx264",
            "-vf", f"scale=-2:{height}",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-start_number", "1",
            "-hls_time", "10",
            "-hls_list_size", "0",
            "-hls_segment_filename", segment_pattern,
            "-f", "hls",
            output_path
        ]

        subprocess.run(cmd, check=True)

        VideoFile.objects.update_or_create(
            video=video,
            resolution=label,
            defaults={
                "file": f"videos/processed/{video.id}/{label}/{playlist_name}"
            }
        )