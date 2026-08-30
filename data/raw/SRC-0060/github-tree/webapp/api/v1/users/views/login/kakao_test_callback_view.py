from django.conf import settings
from django.shortcuts import render

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from common.views import BaseAPIView


class KakaoTestCallbackView(BaseAPIView):
  """
    Kakao OAuth test callback view.
    This view handles the callback from Kakao OAuth and displays the authorization code.
    """

  permission_classes = [AllowAny]
  authentication_classes = []

  @extend_schema(exclude=True)  # Exclude from API documentation
  def get(self, request):
    """
        Handle Kakao OAuth callback and display authorization code.
        """
    code = request.GET.get("code")
    error = request.GET.get("error")
    error_description = request.GET.get("error_description", "")

    if error:
      context = {"error": error, "error_description": error_description}
      return render(request, "kakao_test_callback_error.html", context)

    if not code:
      return render(request, "kakao_test_callback_error.html")

    redirect_uri = getattr(
      settings,
      "KAKAO_TEST_CALLBACK_URI",
      "http://localhost:8000/api/v1/users/kakao/test/callback/",
    )
    context = {"code": code, "redirect_uri": redirect_uri}
    return render(request, "kakao_test_callback_success.html", context)
