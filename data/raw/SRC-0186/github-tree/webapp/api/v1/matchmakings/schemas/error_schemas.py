from drf_spectacular.utils import OpenApiResponse
from rest_framework import status

from common.schemas.error_schemas import get_error_response_schema


def get_referral_not_found_error_schema() -> OpenApiResponse:
    """Get referral not found error response schema"""
    return get_error_response_schema(
        error_code="MTM-404",
        message="Referral not found",
        description="The requested referral could not be found",
        http_status=status.HTTP_404_NOT_FOUND,
        details_example={
            "referral_id": 123,
            "user_id": 456,
        },
    )


def get_referral_validation_error_schema() -> OpenApiResponse:
    """Get referral validation error response schema"""
    return get_error_response_schema(
        error_code="MTM-400",
        message="Referral validation error",
        description="Invalid referral data provided",
        http_status=status.HTTP_400_BAD_REQUEST,
        details_example={
            "field": "algorithm_type",
            "error": "Invalid algorithm type provided",
        },
    )


def get_matching_not_found_error_schema() -> OpenApiResponse:
    """Get matching not found error response schema"""
    return get_error_response_schema(
        error_code="MTM-404",
        message="Matching not found",
        description="The requested matching could not be found",
        http_status=status.HTTP_404_NOT_FOUND,
        details_example={
            "matching_id": 123,
            "user_id": 456,
        },
    )


def get_matching_validation_error_schema() -> OpenApiResponse:
    """Get matching validation error response schema"""
    return get_error_response_schema(
        error_code="MTM-400",
        message="Matching validation error",
        description="Invalid matching data provided",
        http_status=status.HTTP_400_BAD_REQUEST,
        details_example={
            "field": "action",
            "error": "Invalid action provided. Must be 'accept' or 'reject'",
        },
    )


def get_matching_access_denied_error_schema() -> OpenApiResponse:
    """Get matching access denied error response schema"""
    return get_error_response_schema(
        error_code="MTM-403",
        message="Access denied to this matching",
        description="You don't have permission to access this matching",
        http_status=status.HTTP_403_FORBIDDEN,
        details_example={
            "matching_id": 123,
            "user_id": 456,
        },
    )


def get_no_more_referrals_error_schema() -> OpenApiResponse:
    """Get no more referrals available error response schema"""
    return get_error_response_schema(
        error_code="MTM-404",
        message="No more referrals available",
        description="No more referrals are available for the user",
        http_status=status.HTTP_404_NOT_FOUND,
        details_example={
            "user_id": 456,
            "algorithm_type": "compatibility",
        },
    )
