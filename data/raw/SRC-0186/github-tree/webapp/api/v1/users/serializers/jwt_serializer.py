from rest_framework import serializers

from .user_detail_serializer import UserDetailSerializer


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_data = UserDetailSerializer(obj["user"], context=self.context).data
        return user_data
