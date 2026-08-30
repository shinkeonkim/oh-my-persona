from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import BaseAPIException


class ProfileNotFoundError(BaseAPIException):
    """Profile not found exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.PRF_404,
            message=message or "Profile not found",
            details=details,
        )


class ProfileValidationError(BaseAPIException):
    """Profile validation error exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.PRF_422,
            message=message or "Profile validation error",
            details=details,
        )


class FileNotFoundError(BaseAPIException):
    """File not found exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.FILE_404,
            message=message or "File not found",
            details=details,
        )


class FileTooLargeError(BaseAPIException):
    """File too large exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.FILE_413,
            message=message or "File too large",
            details=details,
        )


class UnsupportedFileTypeError(BaseAPIException):
    """Unsupported file type exception"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCodes.FILE_415,
            message=message or "Unsupported file type",
            details=details,
        )
