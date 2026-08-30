from django.contrib import admin
from meme.models import TextMeme

from .meme_admin import MemeAdmin


@admin.register(TextMeme)
class TextMemeAdmin(MemeAdmin):
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["type"] = "Text"
        return initial
