from api.v1.file_manager.serializers import (
    AudioSerializer,
    ThumbnailSerializer,
    VideoSerializer,
)
from api.v1.tag.serializers import TagSerializer
from file_manager.models import Audio, Thumbnail, Video
from meme.models import Meme
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from tag.models import Tag


class MemeSerializer(serializers.ModelSerializer):
    tag_ids = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        write_only=True,
        many=True,
        required=False,
    )
    thumbnail_id = PrimaryKeyRelatedField(
        queryset=Thumbnail.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    audio_id = PrimaryKeyRelatedField(
        queryset=Audio.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    video_id = PrimaryKeyRelatedField(
        queryset=Video.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_bookmarked = serializers.SerializerMethodField()

    tags = TagSerializer(many=True, read_only=True)
    thumbnail = ThumbnailSerializer(read_only=True)
    audio = AudioSerializer(read_only=True)
    video = VideoSerializer(read_only=True)

    def get_is_bookmarked(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return hasattr(obj, "user_bookmarkings") and len(obj.user_bookmarkings) > 0
        return False

    class Meta:
        model = Meme
        fields = [
            "id",
            "title",
            "type",
            "description",
            "thumbnail_id",
            "thumbnail",
            "audio_id",
            "audio",
            "video_id",
            "video",
            "original_title",
            "original_link",
            "tag_ids",
            "tags",
            "is_bookmarked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tags",
            "thumbnail",
            "is_bookmarked",
            "created_at",
            "updated_at",
        ]
