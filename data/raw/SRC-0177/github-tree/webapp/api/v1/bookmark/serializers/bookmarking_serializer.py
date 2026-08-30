from api.v1.meme.serializers import MemeSerializer
from bookmark.models import Bookmark, Bookmarking
from meme.models import Meme
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField


class BookmarkingSerializer(ModelSerializer):
    bookmark_id = PrimaryKeyRelatedField(
        queryset=Bookmark.objects.all(),
        write_only=True,
    )
    meme_id = PrimaryKeyRelatedField(
        queryset=Meme.objects.all(),
        write_only=True,
    )

    meme = MemeSerializer(read_only=True)

    class Meta:
        model = Bookmarking
        fields = [
            "id",
            "bookmark_id",
            "meme_id",
            "meme",
        ]
        read_only_fields = [
            "id",
            "meme",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }
