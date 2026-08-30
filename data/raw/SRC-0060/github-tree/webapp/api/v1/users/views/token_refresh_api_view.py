"""
Token Refresh API View using djangorestframework-simplejwt.

This module provides a token refresh endpoint using simplejwt's built-in
TokenRefreshView, which is the recommended way by both dj-rest-auth and
djangorestframework-simplejwt documentation.

Benefits of using simplejwt's TokenRefreshView:
- Automatic token rotation (if enabled)
- Automatic old token blacklisting (if enabled)
- Proper error handling with standard error codes
- Cookie support for JWT tokens
- Battle-tested implementation
"""

import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView

from ..serializers.token_refresh_request_serializer import (
  TokenRefreshRequestSerializer,
)
from ..serializers.token_refresh_response_serializer import (
  TokenRefreshResponseSerializer,
)

logger = logging.getLogger(__name__)


class TokenRefreshAPIView(SimpleJWTTokenRefreshView):
  """
    Token Refresh API View.

    Uses djangorestframework-simplejwt's TokenRefreshView which automatically:
    - Validates the refresh token
    - Generates a new access token
    - Rotates the refresh token (if ROTATE_REFRESH_TOKENS=True)
    - Blacklists the old refresh token (if BLACKLIST_AFTER_ROTATION=True)
    - Returns both tokens in the response

    This is a thin wrapper around simplejwt's TokenRefreshView to add
    custom serializers and OpenAPI documentation.
    """

  serializer_class = TokenRefreshRequestSerializer

  @extend_schema(
    operation_id="token_refresh",
    tags=["Authentication"],
    summary="Refresh JWT Token",
    description=("Generate a new access token using a valid refresh token.\n\n"
                 "This endpoint uses djangorestframework-simplejwt's built-in functionality:\n"
                 "- Validates the refresh token\n"
                 "- Issues a new access token\n"
                 "- Issues a new refresh token (if token rotation is enabled)\n"
                 "- Blacklists the old refresh token (if configured)\n\n"
                 "**Token Rotation Behavior:**\n"
                 "- If `ROTATE_REFRESH_TOKENS = True`: Returns both new access and refresh tokens\n"
                 "- If `ROTATE_REFRESH_TOKENS = False`: Returns only new access token\n"
                 "- If `BLACKLIST_AFTER_ROTATION = True`: Old refresh token is blacklisted\n\n"
                 "**Current Configuration:**\n"
                 "- Token rotation: Enabled\n"
                 "- Automatic blacklisting: Enabled\n"
                 "- Access token lifetime: 2 hours\n"
                 "- Refresh token lifetime: 1 day\n"),
    request=TokenRefreshRequestSerializer,
    responses={
      200: TokenRefreshResponseSerializer,
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
        name="Token refresh request",
        description="Provide the refresh token to get new tokens",
        value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
        request_only=True,
      ),
      OpenApiExample(
        name="Token refresh response (with rotation)",
        description="Both new access and refresh tokens when rotation is enabled",
        value={
          "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
          "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        response_only=True,
      ),
      OpenApiExample(
        name="Token refresh response (without rotation)",
        description="Only new access token when rotation is disabled",
        value={
          "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        response_only=True,
      ),
    ],
  )
  def post(self, request, *args, **kwargs):
    """
        Handle token refresh request.

        The parent TokenRefreshView (from simplejwt) handles:
        - Token validation
        - Access token generation
        - Token rotation (if enabled)
        - Token blacklisting (if enabled)
        """
    return super().post(request, *args, **kwargs)
