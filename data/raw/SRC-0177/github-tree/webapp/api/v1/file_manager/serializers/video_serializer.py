from file_manager.models import Video
from rest_framework.serializers import ModelSerializer
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class VideoSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["url"]
        
    @extend_schema_field(OpenApiTypes.STR)
    def url(self, obj):
        return obj.url
