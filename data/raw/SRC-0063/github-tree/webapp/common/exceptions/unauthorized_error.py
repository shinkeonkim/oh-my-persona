from .base_api_exception import BaseAPIException
from .common_error_code import CommonErrorCode


class UnauthorizedError(BaseAPIException):
    """Unauthorized error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=CommonErrorCode.COMMON_401,
            message=message or CommonErrorCode.COMMON_401.message,
            details=details,
        )
