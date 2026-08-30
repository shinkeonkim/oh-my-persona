from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from .social_account_serializer import SocialAccountSerializer


class UserDetailSerializer(UserDetailsSerializer):
    """
    UserSerializer를 확장하여 소셜 계정 정보를 포함
    """

    social_account = SocialAccountSerializer(source="socialaccount_set", many=True, read_only=True)
    referral_quota_recover_at = serializers.DateTimeField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = tuple(f for f in UserDetailsSerializer.Meta.fields if f != "pk") + (
            "id",
            "username",
            "real_name",
            "phone_number",
            "social_account",
            "ticket_amount",
            "used_ticket_amount",
            "remaining_referral_quota_count",
            "referral_quota_recover_at",
            "is_intro_completed",
            "is_identity_verified",
            "is_confirmed",
        )

        read_only_fields = tuple(f for f in UserDetailsSerializer.Meta.read_only_fields if f != "pk") + (
            "real_name",
            "phone_number",
            "ticket_amount",
            "used_ticket_amount",
            "remaining_referral_quota_count",
            "referral_quota_recover_at",
            "is_intro_completed",
            "is_identity_verified",
            "is_confirmed",
        )
