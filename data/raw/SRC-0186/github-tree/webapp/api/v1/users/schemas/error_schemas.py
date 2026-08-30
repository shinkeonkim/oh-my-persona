from drf_spectacular.utils import OpenApiResponse
from rest_framework import status

from common.schemas.error_schemas import get_error_response_schema


# User-specific error response schemas
def get_external_service_error_schema() -> OpenApiResponse:
    """Get external service error response schema"""
    return get_error_response_schema(
        error_code="EXT-400",
        message="External service error",
        description="An error occurred with an external service",
        http_status=status.HTTP_400_BAD_REQUEST,
        details_example={
            "service": "Kakao API",
            "error": "Service temporarily unavailable",
        },
    )
