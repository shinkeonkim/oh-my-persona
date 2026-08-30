from django.contrib import admin
from meme.models import AudioMeme

from .meme_admin import MemeAdmin


@admin.register(AudioMeme)
class AudioMemeAdmin(MemeAdmin):
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["type"] = "Audio"
        return initial
