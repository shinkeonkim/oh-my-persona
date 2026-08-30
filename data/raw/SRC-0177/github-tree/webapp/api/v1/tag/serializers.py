from rest_framework import serializers
from tag.models import Tag, TagCategory


class TagCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TagCategory
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    category = TagCategorySerializer()
    popularity = serializers.FloatField(read_only=True, required=False)
    memes_count = serializers.IntegerField(read_only=True, required=False)
    bookmarkings_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "category",
            "popularity",
            "memes_count",
            "bookmarkings_count",
        ]
