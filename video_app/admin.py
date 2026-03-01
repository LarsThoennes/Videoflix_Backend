from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Video, VideoFile


class VideoResource(resources.ModelResource):
    class Meta:
        model = Video


class VideoFileInline(admin.TabularInline):
    model = VideoFile
    extra = 0


@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    inlines = [VideoFileInline]