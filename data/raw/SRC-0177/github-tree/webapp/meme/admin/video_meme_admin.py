from django.contrib import admin
from meme.models import VideoMeme

from .meme_admin import MemeAdmin


@admin.register(VideoMeme)
class VideoMemeAdmin(MemeAdmin):
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["type"] = "Video"
        return initial
