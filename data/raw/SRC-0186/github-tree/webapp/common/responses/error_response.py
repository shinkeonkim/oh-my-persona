from dataclasses import dataclass
from typing import Any, Dict, Optional

from rest_framework.response import Response

from common.enums.error_codes import ErrorCode


@dataclass
class ErrorResponseData:
    """Standardized error response data structure"""

    status: str = "FAIL"
    message: str = ""
    error_code: str = ""
    description: str = ""
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "status": self.status,
            "message": self.message,
            "error_code": self.error_code,
            "description": self.description,
        }
        if self.details:
            result["details"] = self.details
        return result


class ErrorResponse:
    """Standardized error response handler"""

    @staticmethod
    def create_error_response(
        error_code: ErrorCode,
        message: Optional[str] = None,
        description: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None,
    ) -> Response:
        """
        Create a standardized error response

        Args:
            error_code: ErrorCode dataclass instance
            message: Custom error message (optional, uses default if not provided)
            description: Custom description (optional, uses default if not provided)
            details: Additional error details (optional)
            http_status: HTTP status code (optional, uses error_code.http_status if not provided)

        Returns:
            Response: DRF Response object with standardized error format
        """
        # Use provided message or default from error code
        error_message = message or error_code.message
        error_description = description or error_code.description

        # Use provided HTTP status or default from error code
        if http_status is None:
            http_status = error_code.http_status

        # Create error response data
        error_data = ErrorResponseData(
            status="FAIL",
            message=error_message,
            error_code=error_code.code,
            description=error_description,
            details=details,
        )

        return Response(
            data=error_data.to_dict(),
            status=http_status,
        )

    @staticmethod
    def validation_error(
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Create a validation error response"""
        from common.enums.error_codes import ErrorCodes

        return ErrorResponse.create_error_response(
            error_code=ErrorCodes.VAL_422,
            message=message,
            details=details,
        )

    @staticmethod
    def not_found(
        resource: str = "Resource",
        message: Optional[str] = None,
    ) -> Response:
        """Create a not found error response"""
        from common.enums.error_codes import ErrorCodes

        if message is None:
            message = f"{resource} not found"
        return ErrorResponse.create_error_response(
            error_code=ErrorCodes.USR_404,
            message=message,
        )

    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
    ) -> Response:
        """Create an unauthorized error response"""
        from common.enums.error_codes import ErrorCodes

        return ErrorResponse.create_error_response(
            error_code=ErrorCodes.AUTH_401,
            message=message,
        )

    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
    ) -> Response:
        """Create a forbidden error response"""
        from common.enums.error_codes import ErrorCodes

        return ErrorResponse.create_error_response(
            error_code=ErrorCodes.AUTH_403,
            message=message,
        )

    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Create an internal server error response"""
        from common.enums.error_codes import ErrorCodes

        return ErrorResponse.create_error_response(
            error_code=ErrorCodes.SRV_500,
            message=message,
            details=details,
        )
