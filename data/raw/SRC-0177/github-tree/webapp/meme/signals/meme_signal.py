from django.db.models.signals import post_save
from meme.models import AudioMeme, ImageMeme, Meme, MemeCounter, TextMeme, VideoMeme

MEME_MODELS = (Meme, ImageMeme, AudioMeme, TextMeme, VideoMeme)


def create_meme_counter(sender, instance, created, **kwargs):
    if not hasattr(instance, "meme_counter"):
        MemeCounter.objects.create(meme=instance)


for meme_model in MEME_MODELS:
    post_save.connect(create_meme_counter, sender=meme_model)
