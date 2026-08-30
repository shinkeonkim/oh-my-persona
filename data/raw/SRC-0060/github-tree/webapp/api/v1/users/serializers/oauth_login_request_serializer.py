from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers


class OAuthLoginRequestSerializer(SocialLoginSerializer):
  """
    Base serializer for OAuth login request.
    Can be used for any OAuth provider (Kakao, Google, etc.).
    """

  code = serializers.CharField(required=True, help_text="OAuth authorization code received from provider")
  redirect_uri = serializers.URLField(
    required=False,
    allow_blank=True,
    help_text="Redirect URI used in OAuth flow (optional, falls back to default)",
  )
