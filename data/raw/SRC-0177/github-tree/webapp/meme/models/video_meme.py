from meme.models.meme import Meme


class VideoMeme(Meme):
    MEME_TYPE = "Video"

    class Meta:
        proxy = True

    # TODO(koa): video가 무조건 있어야함을 validation으로 추가해야함.

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = "Video"
        super(VideoMeme, self).__init__(*args, **kwargs)
