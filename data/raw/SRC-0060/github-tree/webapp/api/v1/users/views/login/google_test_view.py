from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import render

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from common.views import BaseAPIView


class GoogleTestView(BaseAPIView):
  """
    Google OAuth test page view.
    This view renders a test page for testing Google OAuth flow.
    """

  permission_classes = [AllowAny]
  authentication_classes = []

  @property
  def callback_url(self):
    """
        Get the callback URL for Google OAuth test flow.
        """
    return getattr(
      settings,
      "GOOGLE_TEST_CALLBACK_URI",
      "http://localhost:8000/api/v1/users/google/test/callback/",
    )

  @extend_schema(exclude=True)  # Exclude from API documentation
  def get(self, request):
    """
        Render Google OAuth test page.
        """
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", None)
    redirect_uri = getattr(
      settings,
      "GOOGLE_TEST_CALLBACK_URI",
      "http://localhost:8000/api/v1/users/google/test/callback/",
    )

    if not client_id:
      return render(request, "google_test_config_error.html")

    # Generate Google OAuth authorization URL
    params = {
      "client_id": client_id,
      "redirect_uri": redirect_uri,
      "response_type": "code",
      "scope": "openid profile email",
      "access_type": "offline",
      "prompt": "consent",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    context = {
      "auth_url": auth_url,
      "client_id": client_id,
      "redirect_uri": redirect_uri,
      "scope": "openid profile email",
    }

    return render(request, "google_test.html", context)
