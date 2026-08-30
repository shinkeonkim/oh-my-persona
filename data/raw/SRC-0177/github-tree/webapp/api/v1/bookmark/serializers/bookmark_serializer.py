from bookmark.models import Bookmark
from rest_framework import serializers


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ["id", "title", "bookmarkings_count", "created_at", "updated_at"]
        read_only_fields = ["bookmarkings_count", "created_at", "updated_at"]

    def create(self, validated_data):
        bookmark = Bookmark.objects.create(**validated_data)
        return bookmark

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        return instance
