from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import BaseAPIException


class UserNotFoundError(BaseAPIException):
    """User not found exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.USR_404,
            message=message or "User not found",
            details=details,
        )


class UserValidationError(BaseAPIException):
    """User validation error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.USR_422,
            message=message or "User validation error",
            details=details,
        )


class UserAlreadyExistsError(BaseAPIException):
    """User already exists exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.USR_409,
            message=message or "User already exists",
            details=details,
        )


class InvalidCredentialsError(BaseAPIException):
    """Invalid credentials exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.AUTH_422,
            message=message or "Invalid credentials",
            details=details,
        )


class ExternalServiceError(BaseAPIException):
    """External service error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.EXT_400,
            message=message or "External service error",
            details=details,
        )
