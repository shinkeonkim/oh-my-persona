from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from rest_framework import status


def get_error_response_schema(
    error_code: str,
    message: str,
    description: str,
    http_status: int,
    details_example: dict = None,
) -> OpenApiResponse:
    """
    Generate standardized error response schema for drf-spectacular

    Args:
        error_code: Error code (e.g., "USR-404")
        message: Error message
        description: Detailed description
        http_status: HTTP status code
        details_example: Optional details example

    Returns:
        OpenApiResponse: Formatted error response schema
    """
    response_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Response status",
                "example": "FAIL",
            },
            "message": {
                "type": "string",
                "description": "Error message",
                "example": message,
            },
            "error_code": {
                "type": "string",
                "description": "Error code",
                "example": error_code,
            },
            "description": {
                "type": "string",
                "description": "Detailed error description",
                "example": description,
            },
        },
        "required": ["status", "message", "error_code", "description"],
    }

    if details_example:
        response_schema["properties"]["details"] = {
            "type": "object",
            "description": "Additional error details",
            "example": details_example,
        }

    return OpenApiResponse(
        response=response_schema,
        description=f"Error: {message}",
        examples=[
            OpenApiExample(
                name=f"{error_code} Error",
                value={
                    "status": "FAIL",
                    "message": message,
                    "error_code": error_code,
                    "description": description,
                    **({"details": details_example} if details_example else {}),
                },
                status_codes=[http_status],
            )
        ],
    )


# Common error response schemas - only truly common ones
def get_validation_error_schema() -> OpenApiResponse:
    """Get validation error response schema"""
    return get_error_response_schema(
        error_code="VAL-422",
        message="Validation error",
        description="One or more fields failed validation",
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details_example={"field_errors": {"field_name": ["This field is required."]}},
    )


def get_not_found_error_schema(resource: str = "Resource") -> OpenApiResponse:
    """Get not found error response schema"""
    return get_error_response_schema(
        error_code="SRV-404",
        message=f"{resource} not found",
        description=f"The requested {resource.lower()} does not exist",
        http_status=status.HTTP_404_NOT_FOUND,
    )


def get_unauthorized_error_schema() -> OpenApiResponse:
    """Get unauthorized error response schema"""
    return get_error_response_schema(
        error_code="AUTH-401",
        message="Authentication required",
        description="Authentication credentials were not provided or are invalid",
        http_status=status.HTTP_401_UNAUTHORIZED,
    )


def get_forbidden_error_schema() -> OpenApiResponse:
    """Get forbidden error response schema"""
    return get_error_response_schema(
        error_code="AUTH-403",
        message="Access forbidden",
        description="You do not have permission to access this resource",
        http_status=status.HTTP_403_FORBIDDEN,
    )


def get_internal_server_error_schema() -> OpenApiResponse:
    """Get internal server error response schema"""
    return get_error_response_schema(
        error_code="SRV-500",
        message="Internal server error",
        description="An internal server error occurred",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details_example={"error": "Detailed error information"},
    )
