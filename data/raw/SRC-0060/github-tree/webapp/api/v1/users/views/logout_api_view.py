"""
Logout API View using dj-rest-auth.

This module provides a logout endpoint using dj-rest-auth's built-in LogoutView,
which handles JWT token blacklisting automatically when using simplejwt.

Benefits of using dj-rest-auth's LogoutView:
- Automatic JWT token blacklisting (if enabled)
- Cookie cleanup for JWT cookies
- Session logout support (if enabled)
- Consistent error handling
- Battle-tested implementation
"""

import logging

from dj_rest_auth.views import LogoutView
from drf_spectacular.utils import OpenApiExample, extend_schema

from ..serializers.logout_request_serializer import LogoutRequestSerializer
from ..serializers.logout_response_serializer import LogoutResponseSerializer

logger = logging.getLogger(__name__)


class LogoutAPIView(LogoutView):
  """
    Logout API View.

    Uses dj-rest-auth's LogoutView which automatically:
    - Blacklists the refresh token (when ROTATE_REFRESH_TOKENS=True)
    - Clears JWT cookies (if JWT_AUTH_HTTPONLY=True)
    - Performs Django logout (if SESSION_LOGIN=True)
    - Returns a success response

    This is a thin wrapper around dj-rest-auth's LogoutView to add
    custom OpenAPI documentation.
    """

  serializer_class = LogoutRequestSerializer

  @extend_schema(
    operation_id="logout",
    tags=["Authentication"],
    summary="Logout User",
    description=("Blacklist the refresh token to securely logout the user.\n\n"
                 "This endpoint uses dj-rest-auth's built-in logout functionality:\n"
                 "- Blacklists the JWT refresh token (requires simplejwt token blacklist)\n"
                 "- Clears JWT cookies if configured\n"
                 "- Performs Django session logout if enabled\n\n"
                 "**Requirements:**\n"
                 "- `rest_framework_simplejwt.token_blacklist` must be in INSTALLED_APPS\n"
                 "- `ROTATE_REFRESH_TOKENS = True` in SIMPLE_JWT settings\n"
                 "- `BLACKLIST_AFTER_ROTATION = True` in SIMPLE_JWT settings\n"),
    request=LogoutRequestSerializer,
    responses={
      200: LogoutResponseSerializer,
      400: {
        "description": "Validation error - refresh token not provided",
        "content": {
          "application/json": {
            "example": {
              "refresh": ["This field is required."]
            }
          }
        },
      },
      401: {
        "description": "Invalid or expired token",
        "content": {
          "application/json": {
            "example": {
              "detail": "Token is invalid or expired",
              "code": "token_not_valid"
            }
          }
        },
      },
    },
    examples=[
      OpenApiExample(
        name="Logout request",
        description="Provide the refresh token to blacklist",
        value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
        request_only=True,
      ),
      OpenApiExample(
        name="Successful logout",
        description="Token successfully blacklisted",
        value={"detail": "Successfully logged out."},
        response_only=True,
      ),
    ],
  )
  def post(self, request, *args, **kwargs):
    """
        Handle logout request.

        The parent LogoutView (from dj-rest-auth) handles:
        - Token validation
        - Token blacklisting
        - Cookie cleanup
        - Session logout
        """
    return super().post(request, *args, **kwargs)
