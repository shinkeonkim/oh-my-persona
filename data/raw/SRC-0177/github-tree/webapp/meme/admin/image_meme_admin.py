from django.contrib import admin
from meme.models import ImageMeme

from .meme_admin import MemeAdmin


@admin.register(ImageMeme)
class ImageMemeAdmin(MemeAdmin):
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["type"] = "Image"
        return initial
