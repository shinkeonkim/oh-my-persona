from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .user_detail_serializer import UserDetailSerializer


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()

    @extend_schema_field(UserDetailSerializer)
    def get_user(self, obj) -> dict:
        return UserDetailSerializer(obj["user"], context=self.context).data

    class Meta:
        fields = ["access", "refresh", "user"]
