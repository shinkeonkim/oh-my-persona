from django.contrib.auth import get_user_model

from rest_framework import serializers

from .profile_list_serializer import ProfileListSerializer

User = get_user_model()


class UserProfileListSerializer(serializers.ModelSerializer):
    """사용자 프로필 목록용 시리얼라이저 (간소화)"""

    username = serializers.CharField(read_only=True)
    profile = ProfileListSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile",
        ]
        read_only_fields = [
            "id",
            "username",
            "profile",
        ]
