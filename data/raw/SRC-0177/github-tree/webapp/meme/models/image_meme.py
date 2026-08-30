from meme.models.meme import Meme


class ImageMeme(Meme):
    MEME_TYPE = "Image"

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = "Image"
        super(ImageMeme, self).__init__(*args, **kwargs)
