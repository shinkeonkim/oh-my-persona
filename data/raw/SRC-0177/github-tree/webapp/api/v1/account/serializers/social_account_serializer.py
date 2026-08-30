from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SocialAccountSerializer(serializers.ModelSerializer):
    """
    사용자가 연결한 소셜 계정을 반환하는 Serializer
    """

    class Meta:
        model = SocialAccount
        fields = ("provider", "uid")
        read_only_fields = ("provider", "uid")
