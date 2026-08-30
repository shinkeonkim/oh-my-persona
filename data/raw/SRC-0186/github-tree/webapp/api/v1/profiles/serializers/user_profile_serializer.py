from django.contrib.auth import get_user_model

from rest_framework import serializers

from .public_profile_serializer import ProfileSerializer

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 정보 시리얼라이저"""

    # User 모델의 기본 필드들
    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "profile",
        ]
        read_only_fields = [
            "id",
            "email",
            "username",
            "profile",
        ]
