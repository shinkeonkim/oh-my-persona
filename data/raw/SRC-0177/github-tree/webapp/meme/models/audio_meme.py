from meme.models.meme import Meme


class AudioMeme(Meme):
    MEME_TYPE = "Audio"

    class Meta:
        proxy = True

    # TODO(koa): audio가 무조건 있어야함을 validation으로 추가해야함.

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = "Audio"
        super(AudioMeme, self).__init__(*args, **kwargs)
