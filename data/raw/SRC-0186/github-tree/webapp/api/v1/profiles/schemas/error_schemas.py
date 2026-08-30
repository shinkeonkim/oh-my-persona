from drf_spectacular.utils import OpenApiResponse
from rest_framework import status

from common.schemas.error_schemas import get_error_response_schema


# Profile-specific error response schemas
def get_profile_not_found_error_schema() -> OpenApiResponse:
    """Get profile not found error response schema"""
    return get_error_response_schema(
        error_code="PRF-404",
        message="Profile not found",
        description="The requested profile does not exist",
        http_status=status.HTTP_404_NOT_FOUND,
    )


def get_profile_validation_error_schema() -> OpenApiResponse:
    """Get profile validation error response schema"""
    return get_error_response_schema(
        error_code="PRF-422",
        message="Profile validation error",
        description="The profile data failed validation",
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details_example={"field_errors": {"job": ["Selected job does not belong to the specified job category."]}},
    )


def get_file_not_found_error_schema() -> OpenApiResponse:
    """Get file not found error response schema"""
    return get_error_response_schema(
        error_code="FILE-404",
        message="File not found",
        description="The requested file does not exist",
        http_status=status.HTTP_404_NOT_FOUND,
    )


def get_file_too_large_error_schema() -> OpenApiResponse:
    """Get file too large error response schema"""
    return get_error_response_schema(
        error_code="FILE-413",
        message="File too large",
        description="The uploaded file exceeds the maximum allowed size",
        http_status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        details_example={"max_size": "10MB", "current_size": "15MB"},
    )


def get_unsupported_file_type_error_schema() -> OpenApiResponse:
    """Get unsupported file type error response schema"""
    return get_error_response_schema(
        error_code="FILE-415",
        message="Unsupported file type",
        description="The file type is not supported",
        http_status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        details_example={
            "supported_types": ["image/jpeg", "image/png"],
            "provided_type": "image/gif",
        },
    )
