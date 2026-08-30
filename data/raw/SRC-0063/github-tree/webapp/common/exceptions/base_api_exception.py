from rest_framework.exceptions import APIException

from .common_error_code import CommonErrorCode


class BaseAPIException(APIException):
    """Base API exception with standardized error format"""

    def __init__(
        self,
        error_code: CommonErrorCode,
        message: str = None,
        description: str = None,
        details: dict = None,
        http_status: int = None,
    ):
        self.error_code = error_code
        self.message = message or error_code.message
        self.description = description or error_code.description
        self.details = details
        self.http_status = http_status or error_code.status_code

        super().__init__(self.message)

    def get_full_details(self):
        """Return full error details in standardized format"""
        return {
            "status": "FAIL",
            "message": self.message,
            "error_code": self.error_code.code,
            "description": self.description,
            "details": self.details,
        }
