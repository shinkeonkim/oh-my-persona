from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from file_manager.models import Thumbnail
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class ThumbnailSerializer(ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["url"]

    url = serializers.SerializerMethodField("get_url")

    @extend_schema_field(OpenApiTypes.STR)
    def get_url(self, obj):
        url = self.context["request"].build_absolute_uri(obj.url)

        if "api.memez.party" in url and url.startswith("http://"):
            return url.replace("http://", "https://")
        return url
