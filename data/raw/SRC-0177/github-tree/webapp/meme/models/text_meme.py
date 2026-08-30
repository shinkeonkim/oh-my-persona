from meme.models.meme import Meme


class TextMeme(Meme):
    MEME_TYPE = "Text"

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = "Text"
        super(TextMeme, self).__init__(*args, **kwargs)
