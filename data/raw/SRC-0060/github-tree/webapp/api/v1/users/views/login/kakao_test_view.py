from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import render

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from common.views import BaseAPIView


class KakaoTestView(BaseAPIView):
  """
    Kakao OAuth test page view.
    This view renders a test page for testing Kakao OAuth flow.
    """

  permission_classes = [AllowAny]
  authentication_classes = []

  @extend_schema(exclude=True)  # Exclude from API documentation
  def get(self, request):
    """
        Render Kakao OAuth test page.
        """
    client_id = getattr(settings, "KAKAO_CLIENT_ID", None)
    redirect_uri = getattr(
      settings,
      "KAKAO_TEST_CALLBACK_URI",
      "http://localhost:8000/api/v1/users/kakao/test/callback/",
    )

    if not client_id:
      return render(request, "kakao_test_config_error.html")

    # Generate Kakao OAuth authorization URL
    params = {
      "client_id": client_id,
      "redirect_uri": redirect_uri,
      "response_type": "code",
      "scope": "profile_nickname,profile_image,account_email",
    }

    auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"

    context = {
      "auth_url": auth_url,
      "client_id": client_id,
      "redirect_uri": redirect_uri,
      "scope": "profile_nickname,profile_image,account_email",
    }

    return render(request, "kakao_test.html", context)
