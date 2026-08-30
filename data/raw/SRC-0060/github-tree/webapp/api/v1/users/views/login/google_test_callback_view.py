from django.conf import settings
from django.shortcuts import render

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from common.views import BaseAPIView


class GoogleTestCallbackView(BaseAPIView):
  """
    Google OAuth test callback view.
    This view handles the callback from Google OAuth and displays the authorization code.
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
        Handle Google OAuth callback and display authorization code.
        """
    code = request.GET.get("code")
    error = request.GET.get("error")
    error_description = request.GET.get("error_description", "")

    if error:
      context = {"error": error, "error_description": error_description}
      return render(request, "google_test_callback_error.html", context)

    if not code:
      return render(request, "google_test_callback_error.html")

    redirect_uri = getattr(
      settings,
      "GOOGLE_TEST_CALLBACK_URI",
      "http://localhost:8000/api/v1/users/google/test/callback/",
    )
    context = {"code": code, "redirect_uri": redirect_uri}
    return render(request, "google_test_callback_success.html", context)
