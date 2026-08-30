from .base_api_exception import BaseAPIException
from .common_error_code import CommonErrorCode


class InternalServerError(BaseAPIException):
    """Internal server error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=CommonErrorCode.COMMON_500,
            message=message or CommonErrorCode.COMMON_500.message,
            details=details,
        )
