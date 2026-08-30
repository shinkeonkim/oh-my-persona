from file_manager.models import Audio
from rest_framework.serializers import ModelSerializer
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class AudioSerializer(ModelSerializer):
    class Meta:
        model = Audio
        fields = ["url"]
        
    @extend_schema_field(OpenApiTypes.STR)
    def url(self, obj):
        return obj.url
